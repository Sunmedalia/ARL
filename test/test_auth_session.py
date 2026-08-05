import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from flask import Flask
from werkzeug.security import generate_password_hash

from app import auth_session as auth
from app.utils import gen_md5
from app.utils.user import user_login


class TestAuthSession(unittest.TestCase):
    def test_username_normalization_blocks_unicode_and_case_variants(self):
        self.assertEqual(auth.normalize_username("  ＡＤＭＩＮ  "), "admin")
        self.assertEqual(auth.normalize_username("Admin"), "admin")

    def test_login_limit_covers_username_ip_and_ip_dimensions(self):
        attempts = MagicMock()
        attempts.count_documents.side_effect = [4, auth.IP_ATTEMPT_LIMIT]
        with patch("app.auth_session.conn_db", return_value=attempts):
            self.assertTrue(auth.login_is_limited("ＡＤＭＩＮ", "203.0.113.5"))
        pair_query, ip_query = [call.args[0] for call in attempts.count_documents.call_args_list]
        self.assertEqual(pair_query["username"], "admin")
        self.assertEqual(pair_query["ip"], "203.0.113.5")
        self.assertNotIn("username", ip_query)

    def test_login_uses_normalized_lookup_and_returns_canonical_username(self):
        users = MagicMock()
        user = {"_id": "user-id", "username": "Admin", "password_hash": "hash"}
        users.find_one.side_effect = [None, user]
        with patch("app.utils.user.conn_db", return_value=users), \
                patch("app.utils.user.session_service.client_ip", return_value="203.0.113.7"), \
                patch("app.utils.user.session_service.login_is_limited", return_value=False), \
                patch("app.utils.user.session_service.verify_password", return_value=(True, False)), \
                patch("app.utils.user.session_service.clear_failed_logins"), \
                patch("app.utils.user.session_service.create_session", return_value=("session", "csrf")):
            result = user_login("  ＡＤＭＩＮ ", "secret")
        self.assertEqual(result["username"], "Admin")
        self.assertEqual(users.find_one.call_args_list[0].args[0], {"username_normalized": "admin"})
        self.assertEqual(
            users.find_one.call_args_list[1].args[0]["username"]["$regex"], "^admin$"
        )

    def test_legacy_md5_and_scrypt_passwords(self):
        valid, legacy = auth.verify_password({"password": gen_md5("arlsalt!@#secret")}, "secret")
        self.assertTrue(valid)
        self.assertTrue(legacy)
        valid, legacy = auth.verify_password(
            {"password_hash": generate_password_hash("secret", method="scrypt")}, "secret"
        )
        self.assertTrue(valid)
        self.assertFalse(legacy)

    def test_csrf_is_required_for_cookie_writes(self):
        app = Flask(__name__)
        session = {"csrf_hash": auth._digest("csrf")}
        with app.test_request_context("/", method="POST", headers={"X-CSRF-Token": "wrong"}):
            self.assertFalse(auth.validate_csrf(session))
        with app.test_request_context("/", method="POST", headers={"X-CSRF-Token": "csrf"}):
            self.assertTrue(auth.validate_csrf(session))
        with app.test_request_context("/api/task/stop/1", method="GET"):
            self.assertTrue(auth.request_requires_csrf())
        with app.test_request_context("/api/task/", method="GET"):
            self.assertFalse(auth.request_requires_csrf())

    def test_ai_session_auth_does_not_accept_global_api_key(self):
        app = Flask(__name__)
        with app.test_request_context("/api/ai/status", headers={"Token": "global-key"}), \
                patch("app.auth_session.get_session", return_value=None):
            session, error = auth.session_auth(require_csrf=False)
        self.assertIsNone(session)
        self.assertEqual(error[0]["code"], 401)

    def test_password_upgrade_removes_legacy_hash(self):
        collection = MagicMock()
        with patch("app.auth_session.conn_db", return_value=collection):
            auth.upgrade_password({"_id": "user-id"}, "new secret")
        update = collection.update_one.call_args.args[1]
        self.assertIn("password_hash", update["$set"])
        self.assertEqual(update["$unset"], {"password": ""})

    def test_session_has_absolute_eight_hour_expiry(self):
        app = Flask(__name__)
        collection = MagicMock()
        with app.test_request_context("/", headers={"User-Agent": "test"}), \
                patch("app.auth_session.conn_db", return_value=collection):
            auth.create_session("admin")
        inserted = collection.insert_one.call_args.args[0]
        lifetime = inserted["expires_at"] - inserted["created_at"]
        self.assertEqual(lifetime, auth.SESSION_LIFETIME)

    def test_session_touch_is_throttled_to_five_minutes(self):
        app = Flask(__name__)
        collection = MagicMock()
        now = datetime(2026, 8, 5, 10, 0, 0)
        collection.find_one.return_value = {
            "_id": "session-id", "last_seen_at": now, "expires_at": now + auth.SESSION_LIFETIME
        }
        with app.test_request_context("/", headers={"Cookie": "arl_session=raw"}), \
                patch("app.auth_session.conn_db", return_value=collection), \
                patch("app.auth_session.utcnow", return_value=now):
            auth.get_session(touch=True)
        query = collection.update_one.call_args.args[0]
        self.assertEqual(
            query["$or"][0]["last_seen_at"]["$lte"], now - auth.SESSION_TOUCH_INTERVAL
        )

    def test_cookie_security_attributes(self):
        app = Flask(__name__)
        with app.test_request_context("/"):
            response = app.make_response({"ok": True})
            auth.set_session_cookie(response, "token")
            cookie = response.headers["Set-Cookie"]
        self.assertIn("Secure", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Strict", cookie)
        self.assertNotIn("Max-Age", cookie)


if __name__ == "__main__":
    unittest.main()
