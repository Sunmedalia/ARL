import unittest
from unittest import mock

from app.utils import load_file


class TestLoadFile(unittest.TestCase):
    def test_load_file_opens_runtime_data_read_only(self):
        opened = mock.mock_open(read_data="first\nsecond\n")
        with mock.patch("builtins.open", opened):
            self.assertEqual(load_file("rules.txt"), ["first\n", "second\n"])
        opened.assert_called_once_with("rules.txt", "r", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
