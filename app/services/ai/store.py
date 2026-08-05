import json
from datetime import timedelta

from bson import ObjectId

from app.config import Config
from app.auth_session import utcnow
from app.utils.conn import conn_db


AI_COLLECTIONS = ("ai_conversation", "ai_message", "ai_action", "ai_grant")
SECRET_KEYS = {"api_key", "authorization", "cookie", "csrf_token", "password", "token"}


def ensure_ai_indexes():
    for name in AI_COLLECTIONS:
        conn_db(name).create_index("expires_at", expireAfterSeconds=0)
    conn_db("ai_conversation").create_index([("username", 1), ("updated_at", -1)])
    conn_db("ai_message").create_index([("conversation_id", 1), ("created_at", 1)])
    conn_db("ai_action").create_index([("conversation_id", 1), ("created_at", 1)])
    conn_db("ai_grant").create_index(
        [("conversation_id", 1), ("session_id", 1), ("username", 1)]
    )
    conn_db("ai_stream").create_index("expires_at", expireAfterSeconds=0)


def expires_at():
    return utcnow() + timedelta(days=Config.AI_RETENTION_DAYS)


def to_object_id(value):
    try:
        return ObjectId(value)
    except Exception as exc:
        raise ValueError("invalid conversation id") from exc


def serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat() + ("Z" if value.tzinfo is None else "")
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize(item) for item in value]
    return value


def redact(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in SECRET_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def result_within_limit(value):
    """Return a JSON-safe result no larger than the configured audit/tool cap."""
    clean = serialize(redact(value))
    encoded = json.dumps(clean, ensure_ascii=False, default=str).encode("utf-8")
    if len(encoded) <= Config.AI_MAX_RESULT_BYTES:
        return clean
    if isinstance(clean, dict) and isinstance(clean.get("items"), list):
        clean = dict(clean)
        while clean["items"] and len(json.dumps(clean, ensure_ascii=False).encode("utf-8")) > Config.AI_MAX_RESULT_BYTES:
            clean["items"].pop()
        clean["truncated"] = True
        return clean
    return {"truncated": True, "message": "tool result exceeded the 50KB limit"}


def create_conversation(username, session_id, title):
    now = utcnow()
    item = {
        "username": username,
        "session_id": session_id,
        "title": title[:120] or "新对话",
        "created_at": now,
        "updated_at": now,
        "expires_at": expires_at(),
    }
    conn_db("ai_conversation").insert_one(item)
    return str(item["_id"])


def get_conversation(conversation_id, username, session_id=None):
    query = {"_id": to_object_id(conversation_id), "username": username}
    if session_id is not None:
        query["session_id"] = session_id
    return conn_db("ai_conversation").find_one(query)


def add_message(conversation_id, role, content, **extra):
    item = {
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": utcnow(),
        "expires_at": expires_at(),
    }
    item.update(redact(extra))
    conn_db("ai_message").insert_one(item)
    conn_db("ai_conversation").update_one(
        {"_id": to_object_id(conversation_id)},
        {"$set": {"updated_at": utcnow(), "expires_at": expires_at()}},
    )
    return item


def audit_action(conversation_id, username, session_id, tool_name, arguments,
                 result, status, duration_ms, authorized=False):
    item = {
        "conversation_id": conversation_id,
        "username": username,
        "session_id": session_id,
        "tool_name": tool_name,
        "arguments": result_within_limit(redact(arguments)),
        "result": result_within_limit(result),
        "status": status,
        "duration_ms": duration_ms,
        "authorized": authorized,
        "created_at": utcnow(),
        "expires_at": expires_at(),
    }
    conn_db("ai_action").insert_one(item)
    return item


def grant_exists(conversation_id, username, session_id):
    return bool(conn_db("ai_grant").find_one({
        "conversation_id": conversation_id,
        "username": username,
        "session_id": session_id,
        "revoked_at": None,
        "expires_at": {"$gt": utcnow()},
    }))
