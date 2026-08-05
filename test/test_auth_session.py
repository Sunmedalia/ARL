import unittest
from unittest.mock import MagicMock, patch

from flask import Flask
from werkzeug.security import generate_password_hash

from app import auth_session as auth
from app.utils import gen_md5


class TestAuthSession(unittest.TestCase):
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
