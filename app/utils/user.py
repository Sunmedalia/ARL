import functools
import re

from flask import request
from werkzeug.security import generate_password_hash

from app.config import Config
from app import auth_session as session_service
from . import gen_md5, random_choices
from .conn import conn_db


salt = "arlsalt!@#"


def user_login(username=None, password=None):
    username_normalized = session_service.normalize_username(username)
    if not username_normalized or len(username_normalized) > 128 or not password:
        return None
    ip = session_service.client_ip()
    if session_service.login_is_limited(username_normalized, ip):
        return {"_error": "too many login attempts", "_status": 429}

    users = conn_db("user")
    user = users.find_one({"username_normalized": username_normalized})
    if not user:
        user = users.find_one({
            "username": {"$regex": "^{}$".format(re.escape(username_normalized)), "$options": "i"}
        })
    if not user:
        # One legacy administrator can predate the normalized lookup field.
        # The collection is intentionally tiny, so this bounded migration
        # fallback safely handles Unicode compatibility forms once.
        for candidate in users.find({}, {"username": 1, "password": 1, "password_hash": 1}):
            if session_service.normalize_username(candidate.get("username")) == username_normalized:
                user = candidate
                break
    valid, legacy = session_service.verify_password(user or {}, password)
    if not valid:
        session_service.record_failed_login(username_normalized, ip)
        return None

    canonical_username = user.get("username", username_normalized)
    session_service.clear_failed_logins(username_normalized, ip)
    users.update_one({"_id": user["_id"]}, {"$set": {
        "username_normalized": session_service.normalize_username(canonical_username)
    }})
    if legacy:
        session_service.upgrade_password(user, password)

    # Keep issuing the historical header token for one migration cycle.  It is
    # never accepted by the AI service.
    legacy_token = gen_md5(random_choices(50))
    users.update_one({"_id": user["_id"]}, {"$set": {"token": legacy_token}})
    session_token, csrf_token = session_service.create_session(canonical_username)
    return {
        "username": canonical_username,
        "token": legacy_token,
        "type": "login",
        "csrf_token": csrf_token,
        "_session_token": session_token,
    }


def user_login_header():
    """Authenticate a legacy header/API caller or a browser session."""
    token = request.headers.get("Token") or request.args.get("token")
    if token:
        if token == Config.API_KEY and Config.API_KEY:
            return {"username": "ARL-API", "token": token, "type": "api"}
        data = conn_db("user").find_one({"token": token})
        if data:
            return {"username": data.get("username"), "token": token, "type": "login"}

    session = session_service.get_session()
    if session:
        return {
            "username": session.get("username"),
            "token": str(session.get("_id")),
            "type": "session",
            "session": session,
        }

    if not Config.AUTH:
        return True
    return False


def user_logout(token=None):
    session_service.revoke_session()
    if token:
        conn_db("user").update_one({"token": token}, {"$set": {"token": None}})


def change_pass(token, old_password, new_password):
    identity = user_login_header()
    if not identity or identity is True:
        return False
    username = identity.get("username")
    if username == "ARL-API":
        return False
    user = conn_db("user").find_one({"username": username})
    valid, _ = session_service.verify_password(user or {}, old_password)
    if not valid:
        return False
    conn_db("user").update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": generate_password_hash(new_password, method="scrypt")},
         "$unset": {"password": ""}},
    )
    return True


def auth(func):
    """ARL API authentication with CSRF protection for cookie writes."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        identity = user_login_header()
        if Config.AUTH and not identity:
            return {"message": "not login", "code": 401, "data": {}}, 401
        if isinstance(identity, dict) and identity.get("type") == "session":
            if session_service.request_requires_csrf():
                if not session_service.validate_csrf(identity["session"]):
                    return {"message": "invalid csrf token", "code": 403, "data": {}}, 403
        return func(*args, **kwargs)
    return wrapper
