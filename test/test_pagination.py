import unittest
from unittest.mock import MagicMock, patch

from werkzeug.exceptions import BadRequest

from app.routes import ARLResource, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


class TestPagination(unittest.TestCase):
    def test_status_and_identifier_filters_are_exact_for_index_use(self):
        query = ARLResource().build_db_query({"status": "done", "task_id": "task"})
        self.assertEqual(query, {"status": "done", "task_id": "task"})

    def test_default_and_maximum_page_size(self):
        resource = ARLResource()
        self.assertEqual(resource.get_default_field({})["size"], DEFAULT_PAGE_SIZE)
        self.assertEqual(resource.get_default_field({"size": MAX_PAGE_SIZE})["size"], MAX_PAGE_SIZE)

    def test_invalid_page_and_oversized_page_are_rejected(self):
        resource = ARLResource()
        with self.assertRaises(BadRequest):
            resource.get_default_field({"size": MAX_PAGE_SIZE + 1})
        with self.assertRaises(BadRequest):
            resource.get_default_field({"size": 0})
        with self.assertRaises(BadRequest):
            resource.get_default_field({"page": 0})

    def test_export_ignores_list_pagination_cap(self):
        resource = ARLResource()
        collection = MagicMock()
        collection.find.return_value = [{"domain": "example.com"}]
        with patch("app.routes.conn", return_value=collection), \
                patch.object(resource, "send_file", return_value="response") as send_file:
            result = resource.send_export_file(
                {"domain": "example", "page": 9, "size": 100000}, "domain"
            )
        self.assertEqual(result, "response")
        collection.find.assert_called_once()
        query = collection.find.call_args.args[0]
        self.assertNotIn("page", query)
        self.assertNotIn("size", query)
        send_file.assert_called_once_with({"example.com"}, "domain")


if __name__ == "__main__":
    unittest.main()
