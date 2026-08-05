from flask_restx import Resource, Api, reqparse, fields, Namespace
from bson import ObjectId
from app.utils import get_logger, auth
from app import utils
from app.modules import ErrorMsg
from . import base_query_fields, ARLResource, get_arl_parser

ns = Namespace('service', description="系统服务信息")

logger = get_logger()

base_search_fields = {
    'service_name': fields.String(description="系统服务名称"),
    'service_info.ip': fields.String(required=False, description="IP"),
    'service_info.port_id': fields.Integer(description="端口号"),
    'service_info.version': fields.String(description="系统服务版本"),
    'service_info.product': fields.String(description="产品"),
    "task_id": fields.String(description="任务ID")
}

base_search_fields.update(base_query_fields)


@ns.route('/')
class ARLService(ARLResource):
    parser = get_arl_parser(base_search_fields, location='args')

    @auth
    @ns.expect(parser)
    def get(self):
        """
        服务信息查询
        """
        args = self.parser.parse_args()
        data = self.build_data(args=args, collection='service')

        return data


@ns.route('/export/')
class ARLServiceExport(ARLResource):
    parser = get_arl_parser(base_search_fields, location='args')

    @auth
    @ns.expect(parser)
    def get(self):
        return self.send_jsonl_export(self.parser.parse_args(), 'service')


delete_service_fields = ns.model('deleteServiceFields', {
    '_id': fields.List(fields.String(required=True, description='服务 _id'))
})


@ns.route('/delete/')
class DeleteARLService(ARLResource):
    @auth
    @ns.expect(delete_service_fields)
    def post(self):
        args = self.parse_args(delete_service_fields)
        id_list = args.pop('_id', [])
        for item_id in id_list:
            utils.conn_db('service').delete_one({'_id': ObjectId(item_id)})
        return utils.build_ret(ErrorMsg.Success, {'_id': id_list})
