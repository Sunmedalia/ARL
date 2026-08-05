import unittest
from unittest.mock import MagicMock, patch

from app.utils.arlupdate import QUERY_INDEXES, ensure_query_indexes
from arl_tool.explain_indexes import uses_index


class TestQueryIndexes(unittest.TestCase):
    def test_task_scope_status_indexes_include_default_id_sort(self):
        self.assertIn([("status", 1), ("_id", -1)], QUERY_INDEXES["task"])
        self.assertIn([("task_id", 1), ("_id", -1)], QUERY_INDEXES["domain"])
        self.assertIn([("scope_id", 1), ("_id", -1)], QUERY_INDEXES["asset_site"])

    def test_query_indexes_are_created_idempotently(self):
        collections = {}

        def fake_conn(name):
            return collections.setdefault(name, MagicMock())

        with patch("app.utils.arlupdate.conn_db", side_effect=fake_conn):
            ensure_query_indexes()
        for name, indexes in QUERY_INDEXES.items():
            actual = [call.args[0] for call in collections[name].create_index.call_args_list]
            self.assertEqual(actual, indexes)

    def test_explain_validator_detects_index_scan(self):
        self.assertTrue(uses_index({"stage": "FETCH", "inputStage": {"stage": "IXSCAN"}}))
        self.assertFalse(uses_index({"stage": "COLLSCAN"}))


if __name__ == "__main__":
    unittest.main()
