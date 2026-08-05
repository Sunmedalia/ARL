"""Server-side administrator sessions used by the web and AI applications.

The legacy ``Token`` header remains supported by :func:`app.utils.user.auth`, but
browser authentication is deliberately kept here so that the AI process never
has to accept the global ARL API key.
"""

import hashlib
import hmac
import secrets
import unicodedata
from datetime import datetime, timedelta

from flask import request
from werkzeug.security import check_password_hash, generate_password_hash

from app.utils.conn import conn_db


SESSION_COOKIE = "arl_session"
SESSION_LIFETIME = timedelta(hours=8)
ATTEMPT_WINDOW = timedelta(minutes=15)
ATTEMPT_LIMIT = 5
IP_ATTEMPT_LIMIT = 20
SESSION_TOUCH_INTERVAL = timedelta(minutes=5)
WRITE_GET_SEGMENTS = (
    "/add", "/delete", "/disable", "/enable", "/logout", "/restart",
    "/run", "/save_", "/stop", "/sync", "/update",
)


def utcnow():
    return datetime.utcnow()


def _digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def ensure_auth_indexes():
    conn_db("auth_session").create_index("expires_at", expireAfterSeconds=0)
    conn_db("auth_session").create_index("token_hash", unique=True)
    conn_db("auth_attempt").create_index("expires_at", expireAfterSeconds=0)
    conn_db("auth_attempt").create_index([("username", 1), ("ip", 1), ("created_at", -1)])
    conn_db("auth_attempt").create_index([("ip", 1), ("created_at", -1)])
    conn_db("user").create_index("username_normalized")


def normalize_username(username):
    if not isinstance(username, str):
        return ""
    return unicodedata.normalize("NFKC", username).strip().casefold()


def client_ip():
    forwarded = request.headers.get("X-Forwarded-For", "").split(",", 1)[0].strip()
    # Shipped Nginx configuration overwrites X-Real-IP, while an arbitrary
    # client could supply X-Forwarded-For unchanged.
    return request.headers.get("X-Real-IP") or forwarded or request.remote_addr or "unknown"


def login_is_limited(username, ip=None):
    username = normalize_username(username)
    ip = ip or client_ip()
    cutoff = utcnow() - ATTEMPT_WINDOW
    attempts = conn_db("auth_attempt")
    pair_limited = attempts.count_documents({
        "username": username,
        "ip": ip,
        "created_at": {"$gte": cutoff},
    }) >= ATTEMPT_LIMIT
    ip_limited = attempts.count_documents({
        "ip": ip,
        "created_at": {"$gte": cutoff},
    }) >= IP_ATTEMPT_LIMIT
    return pair_limited or ip_limited


def record_failed_login(username, ip=None):
    now = utcnow()
    conn_db("auth_attempt").insert_one({
        "username": normalize_username(username),
        "ip": ip or client_ip(),
        "created_at": now,
        "expires_at": now + ATTEMPT_WINDOW,
    })


def clear_failed_logins(username, ip=None):
    conn_db("auth_attempt").delete_many({
        "username": normalize_username(username), "ip": ip or client_ip()
    })


def verify_password(user, password):
    """Verify either a Werkzeug hash or the historical salted MD5 value."""
    password_hash = user.get("password_hash")
    if password_hash:
        try:
            return check_password_hash(password_hash, password), False
        except (ValueError, TypeError):
            return False, False

    from app.utils import gen_md5
    legacy = gen_md5("arlsalt!@#" + password)
    return hmac.compare_digest(str(user.get("password", "")), legacy), True


def upgrade_password(user, password):
    conn_db("user").update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": generate_password_hash(password, method="scrypt")},
         "$unset": {"password": ""}},
    )


def create_session(username):
    ensure_auth_indexes()
    raw_token = secrets.token_urlsafe(48)
    csrf_token = secrets.token_urlsafe(32)
    now = utcnow()
    conn_db("auth_session").insert_one({
        "token_hash": _digest(raw_token),
        "csrf_hash": _digest(csrf_token),
        "csrf_token": csrf_token,
        "username": username,
        "created_at": now,
        "last_seen_at": now,
        "expires_at": now + SESSION_LIFETIME,
        "revoked_at": None,
        "ip": client_ip(),
        "user_agent": request.headers.get("User-Agent", "")[:500],
    })
    return raw_token, csrf_token


def set_session_cookie(response, raw_token):
    response.set_cookie(
        SESSION_COOKIE,
        raw_token,
        secure=True,
        httponly=True,
        samesite="Strict",
        path="/",
    )


def clear_session_cookie(response):
    response.delete_cookie(
        SESSION_COOKIE,
        secure=True,
        httponly=True,
        samesite="Strict",
        path="/",
    )


def get_session(touch=True):
    raw_token = request.cookies.get(SESSION_COOKIE)
    if not raw_token:
        return None
    now = utcnow()
    item = conn_db("auth_session").find_one({
        "token_hash": _digest(raw_token),
        "revoked_at": None,
        "expires_at": {"$gt": now},
    })
    if item and touch:
        conn_db("auth_session").update_one(
            {
                "_id": item["_id"],
                "$or": [
                    {"last_seen_at": {"$lte": now - SESSION_TOUCH_INTERVAL}},
                    {"last_seen_at": {"$exists": False}},
                ],
            },
            {"$set": {"last_seen_at": now}},
        )
    return item


def revoke_session(session=None):
    session = session or get_session(touch=False)
    if session:
        conn_db("auth_session").update_one(
            {"_id": session["_id"]}, {"$set": {"revoked_at": utcnow()}}
        )


def validate_csrf(session):
    supplied = request.headers.get("X-CSRF-Token", "")
    expected = session.get("csrf_hash", "") if session else ""
    return bool(supplied and expected and hmac.compare_digest(_digest(supplied), expected))


def request_requires_csrf():
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        return True
    # A few historical ARL routes mutate state with GET.  Header/API clients
    # stay compatible, while cookie callers must prove same-session intent.
    return request.method == "GET" and any(segment in request.path.lower()
                                           for segment in WRITE_GET_SEGMENTS)


def csrf_token_for_session(session):
    """Return the per-session CSRF token (create it for migrated sessions)."""
    if session.get("csrf_token"):
        return session["csrf_token"]
    token = secrets.token_urlsafe(32)
    conn_db("auth_session").update_one(
        {"_id": session["_id"]},
        {"$set": {"csrf_hash": _digest(token), "csrf_token": token}},
    )
    return token


def session_auth(require_csrf=True):
    session = get_session()
    if not session:
        return None, ({"code": 401, "message": "not login", "data": {}}, 401)
    if require_csrf and request_requires_csrf():
        if not validate_csrf(session):
            return None, ({"code": 403, "message": "invalid csrf token", "data": {}}, 403)
    return session, None
