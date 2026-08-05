from flask import make_response, request
from flask_restx import fields, Namespace
from app.utils import get_logger
from app import utils
from . import  ARLResource
from app import modules
from app import auth_session as session_service

ns = Namespace('user', description="管理员登录认证")

logger = get_logger()



login_fields = ns.model('LoginARL', {
    'username': fields.String(required=True, description="用户名"),
    'password': fields.String(required=True, description="密码"),
})


@ns.route('/login')
class LoginARL(ARLResource):

    @ns.expect(login_fields)
    def post(self):
        """
        用户登录
        """
        args = self.parse_args(login_fields)


        data = utils.user_login(**args)
        if data and data.get("_error"):
            status = data.pop("_status", 429)
            message = data.pop("_error")
            return {"message": message, "code": status, "data": {}}, status
        session_token = data.pop("_session_token") if data else None
        response_data = build_data(data)
        status = 200 if data else 401
        response = make_response(response_data, status)
        if data:
            session_service.set_session_cookie(response, session_token)
        return response




@ns.route('/logout')
class LogoutARL(ARLResource):

    @utils.auth
    def get(self):
        """
        用户退出
        """
        token = request.headers.get("Token")
        utils.user_logout(token)

        response = make_response(build_data({"logged_out": True}))
        session_service.clear_session_cookie(response)
        return response

    def post(self):
        session, error = session_service.session_auth(require_csrf=True)
        if error:
            return error
        utils.user_logout(request.headers.get("Token"))
        response = make_response(build_data({"logged_out": True}))
        session_service.clear_session_cookie(response)
        return response


@ns.route('/session')
class UserSession(ARLResource):
    def get(self):
        session, error = session_service.session_auth(require_csrf=False)
        if error:
            return error
        csrf_token = session_service.csrf_token_for_session(session)
        conversation_id = request.args.get("conversation_id")
        grant_query = {
            "session_id": str(session["_id"]),
            "username": session["username"],
            "revoked_at": None,
            "expires_at": {"$gt": session_service.utcnow()},
        }
        if conversation_id:
            grant_query["conversation_id"] = conversation_id
        granted = bool(conversation_id and utils.conn_db("ai_grant").find_one(grant_query))
        return {
            "code": 200,
            "message": "success",
            "data": {
                "username": session["username"],
                "csrf_token": csrf_token,
                "ai_granted": granted,
                "session_expires_at": session["expires_at"].isoformat() + "Z",
            },
        }


change_pass_fields = ns.model('ChangePassARL', {
    'old_password': fields.String(required=True, description="旧密码"),
    'new_password': fields.String(required=True, description="新密码"),
    'check_password': fields.String(required=True, description="确认密码"),
})


@ns.route('/change_pass')
class ChangePassARL(ARLResource):
    @utils.auth
    @ns.expect(change_pass_fields)
    def post(self):
        """
        密码修改
        """
        args = self.parse_args(change_pass_fields)
        ret = {
            "message": "success",
            "code": 200,
            "data": {}
        }
        token = request.headers.get("Token")

        if args["new_password"] != args["check_password"]:
            ret["code"] = 301
            ret["message"] = "新密码和确定密码不一致"
            return ret

        if not args["new_password"]:
            ret["code"] = 302
            ret["message"] = "新密码不能为空"
            return ret

        if utils.change_pass(token, args["old_password"], args["new_password"]):
            utils.user_logout(token)
        else:
            ret["message"] = "旧密码错误"
            ret["code"] = 303

        return ret


def build_data(data):
    ret = {
        "message": "success",
        "code": 200,
        "data": {}
    }

    if data:
        ret["data"] = data
    else:
        ret["code"] = 401

    return ret
