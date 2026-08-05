import json
import os
from datetime import timedelta

from pymongo.errors import DuplicateKeyError
from flask import Blueprint, Response, request, stream_with_context

from app.config import Config
from app import auth_session as session_service
from app.services.ai import AIChatService, ensure_ai_indexes
from app.services.ai import store
from app.utils.conn import conn_db


ai_blueprint = Blueprint("ai", __name__, url_prefix="/api/ai")


def response(data=None, code=200, message="success"):
    return {"code": code, "message": message, "data": data or {}}, code


def session_required(csrf=False):
    return session_service.session_auth(require_csrf=csrf)


def _conversation_or_error(conversation_id, session):
    try:
        conversation = store.get_conversation(
            conversation_id, session["username"]
        )
    except ValueError:
        conversation = None
    if not conversation:
        return None, response(code=404, message="conversation not found")
    return conversation, None


@ai_blueprint.get("/status")
def status():
    _, error = session_required()
    if error:
        return error
    key_configured = bool(os.environ.get("ARL_AI_API_KEY"))
    available = bool(Config.AI_ENABLED and Config.AI_MODEL and key_configured)
    reason = ""
    if not Config.AI_ENABLED:
        reason = "AI 功能未启用"
    elif not Config.AI_MODEL:
        reason = "未配置 AI 模型"
    elif not key_configured:
        reason = "未设置 ARL_AI_API_KEY"
    return response({
        "enabled": Config.AI_ENABLED,
        "available": available,
        "model": Config.AI_MODEL,
        "base_url": Config.AI_BASE_URL,
        "reason": reason,
    })


@ai_blueprint.get("/conversations")
def conversations():
    session, error = session_required()
    if error:
        return error
    limit = min(max(request.args.get("limit", 30, type=int), 1), 50)
    cursor = conn_db("ai_conversation").find({
        "username": session["username"]
    }).sort("updated_at", -1).limit(limit)
    items = [store.serialize(item) for item in cursor]
    return response({"items": items})


@ai_blueprint.get("/conversations/<conversation_id>")
def conversation_detail(conversation_id):
    session, error = session_required()
    if error:
        return error
    conversation, error = _conversation_or_error(conversation_id, session)
    if error:
        return error
    messages = [store.serialize(item) for item in conn_db("ai_message").find(
        {"conversation_id": conversation_id}
    ).sort("created_at", 1).limit(200)]
    actions = [store.serialize(item) for item in conn_db("ai_action").find(
        {"conversation_id": conversation_id, "username": session["username"]}
    ).sort("created_at", 1).limit(200)]
    granted = store.grant_exists(conversation_id, session["username"], str(session["_id"]))
    return response({"conversation": store.serialize(conversation), "messages": messages,
                     "actions": actions, "granted": granted})


@ai_blueprint.delete("/conversations/<conversation_id>")
def delete_conversation(conversation_id):
    session, error = session_required(csrf=True)
    if error:
        return error
    conversation, error = _conversation_or_error(conversation_id, session)
    if error:
        return error
    conn_db("ai_conversation").delete_one({"_id": conversation["_id"]})
    for collection in ("ai_message", "ai_action", "ai_grant"):
        conn_db(collection).delete_many({"conversation_id": conversation_id})
    return response({"conversation_id": conversation_id})


@ai_blueprint.post("/grant")
def grant():
    session, error = session_required(csrf=True)
    if error:
        return error
    body = request.get_json(silent=True) or {}
    conversation_id = body.get("conversation_id", "")
    _, error = _conversation_or_error(conversation_id, session)
    if error:
        return error
    ensure_ai_indexes()
    query = {"conversation_id": conversation_id, "username": session["username"],
             "session_id": str(session["_id"])}
    now = session_service.utcnow()
    conn_db("ai_grant").update_one(query, {"$set": {
        **query, "granted_at": now, "revoked_at": None,
        "expires_at": min(session["expires_at"], store.expires_at()),
    }}, upsert=True)
    store.audit_action(conversation_id, session["username"], str(session["_id"]),
                       "authorization_granted", {}, {"granted": True}, "success", 0, True)
    return response({"conversation_id": conversation_id, "granted": True})


@ai_blueprint.delete("/grant")
def revoke_grant():
    session, error = session_required(csrf=True)
    if error:
        return error
    body = request.get_json(silent=True) or {}
    conversation_id = body.get("conversation_id", "")
    query = {"conversation_id": conversation_id, "username": session["username"],
             "session_id": str(session["_id"]), "revoked_at": None}
    conn_db("ai_grant").update_many(query, {"$set": {"revoked_at": session_service.utcnow()}})
    if conversation_id:
        store.audit_action(conversation_id, session["username"], str(session["_id"]),
                           "authorization_revoked", {}, {"granted": False}, "success", 0, False)
    return response({"conversation_id": conversation_id, "granted": False})


def _sse(event):
    return "event: {}\ndata: {}\n\n".format(
        event["event"], json.dumps(event.get("data", {}), ensure_ascii=False, default=str)
    )


def _acquire_stream(session_id):
    collection = conn_db("ai_stream")
    now = session_service.utcnow()
    collection.delete_many({"session_id": session_id, "expires_at": {"$lte": now}})
    for slot in range(Config.AI_MAX_STREAMS_PER_SESSION):
        stream_id = "{}:{}".format(session_id, slot)
        try:
            collection.insert_one({
                "_id": stream_id, "session_id": session_id,
                "expires_at": now + timedelta(seconds=Config.AI_TIMEOUT + 30),
            })
            return stream_id
        except DuplicateKeyError:
            continue
    return None


def _renew_stream(stream_id):
    conn_db("ai_stream").update_one(
        {"_id": stream_id},
        {"$set": {"expires_at": session_service.utcnow() +
                  timedelta(seconds=Config.AI_TIMEOUT + 30)}},
    )


@ai_blueprint.post("/chat/stream")
def chat_stream():
    session, error = session_required(csrf=True)
    if error:
        return error
    if not Config.AI_ENABLED or not Config.AI_MODEL or not os.environ.get("ARL_AI_API_KEY"):
        return response(code=503, message="AI service is not configured")
    body = request.get_json(silent=True) or {}
    message = body.get("message")
    if not isinstance(message, str) or not message.strip() or len(message) > 20000:
        return response(code=400, message="message is required and must not exceed 20000 characters")
    message = message.strip()
    conversation_id = body.get("conversation_id")
    if conversation_id:
        _, error = _conversation_or_error(conversation_id, session)
        if error:
            return error
    else:
        ensure_ai_indexes()
        conversation_id = store.create_conversation(
            session["username"], str(session["_id"]), message
        )

    stream_key = _acquire_stream(str(session["_id"]))
    if not stream_key:
        return response(code=429, message="too many concurrent AI streams")

    @stream_with_context
    def generate():
        try:
            service = AIChatService()
            for event in service.stream(
                conversation_id, session["username"], str(session["_id"]), message
            ):
                _renew_stream(stream_key)
                yield _sse(event)
        except GeneratorExit:
            raise
        except Exception:
            yield _sse({"event": "error", "data": {"message": "AI stream failed"}})
        finally:
            conn_db("ai_stream").delete_one({"_id": stream_key})

    return Response(generate(), content_type="text/event-stream", headers={
        "Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no",
    })
