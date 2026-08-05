"""Idempotent database initialization for Docker Compose deployments."""

import os

from werkzeug.security import generate_password_hash

from app.utils import arl_update
from app.utils.conn import conn_db


def main():
    username = os.environ.get("ARL_ADMIN_USERNAME", "admin").strip()
    password = os.environ.get("ARL_ADMIN_PASSWORD", "arlpass")
    if not username or not password:
        raise SystemExit("ARL administrator username and password must not be empty")

    users = conn_db("user")
    users.create_index("username", unique=True)
    existing = users.find_one({"username": username})
    if existing:
        print("ARL administrator already exists; keeping the current password")
    else:
        users.insert_one({
            "username": username,
            "password_hash": generate_password_hash(password, method="scrypt"),
            "token": None,
        })
        print("ARL administrator created: {}".format(username))

    arl_update()
    print("ARL database indexes and runtime data are ready")


if __name__ == "__main__":
    main()
