"""Idempotent database initialization for Docker Compose deployments."""

import os

from werkzeug.security import generate_password_hash

from app.utils import arl_update
from app.utils.conn import conn_db
from app.auth_session import normalize_username


def main():
    username = os.environ.get("ARL_ADMIN_USERNAME", "admin").strip()
    password = os.environ.get("ARL_ADMIN_PASSWORD", "arlpass")
    if not username or not password:
        raise SystemExit("ARL administrator username and password must not be empty")

    users = conn_db("user")
    users.create_index("username", unique=True)
    username_normalized = normalize_username(username)
    existing = users.find_one({"username_normalized": username_normalized})
    if not existing:
        existing = users.find_one({"username": username})
    if existing:
        existing_query = ({"_id": existing["_id"]} if existing.get("_id") else {
            "username": existing["username"]
        })
        users.update_one(existing_query, {"$set": {
            "username_normalized": normalize_username(existing["username"])
        }})
        print("ARL administrator already exists; keeping the current password")
    else:
        users.insert_one({
            "username": username,
            "username_normalized": username_normalized,
            "password_hash": generate_password_hash(password, method="scrypt"),
            "token": None,
        })
        print("ARL administrator created: {}".format(username))

    arl_update()
    print("ARL database indexes and runtime data are ready")


if __name__ == "__main__":
    main()
