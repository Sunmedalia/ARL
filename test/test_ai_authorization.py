import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from app.routes.ai import conversations, revoke_grant
from app.services.ai import store


class TestAIAuthorization(unittest.TestCase):
    def test_conversation_list_rejects_page_size_over_100(self):
        app = Flask(__name__)
        session = {"_id": "session-id", "username": "admin"}
        with app.test_request_context("/api/ai/conversations?size=101"), \
                patch("app.routes.ai.session_required", return_value=(session, None)), \
                patch("app.routes.ai.conn_db") as conn_db:
            result = conversations()
        self.assertEqual(result[1], 400)
        conn_db.assert_not_called()

    def test_revoke_requires_owned_conversation(self):
        app = Flask(__name__)
        grants = MagicMock()
        session = {"_id": "session-id", "username": "admin"}
        with app.test_request_context(
            "/api/ai/grant", method="DELETE", json={"conversation_id": "missing"}
        ), patch("app.routes.ai.session_required", return_value=(session, None)), \
                patch("app.routes.ai.store.get_conversation", return_value=None), \
                patch("app.routes.ai.conn_db", return_value=grants):
            result = revoke_grant()
        self.assertEqual(result[1], 404)
        grants.update_many.assert_not_called()

    def test_conversation_lookup_is_cross_session_but_username_scoped(self):
        collection = MagicMock()
        collection.find_one.return_value = {"username": "admin"}
        conversation_id = "64b64c61f01234567890abcd"
        with patch("app.services.ai.store.conn_db", return_value=collection):
            store.get_conversation(conversation_id, "admin")
        query = collection.find_one.call_args.args[0]
        self.assertEqual(query["username"], "admin")
        self.assertNotIn("session_id", query)


if __name__ == "__main__":
    unittest.main()
