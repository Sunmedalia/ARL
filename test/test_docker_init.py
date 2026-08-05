import os
import unittest
from unittest import mock

from werkzeug.security import check_password_hash

from app import docker_init


class TestDockerInit(unittest.TestCase):
    @mock.patch.object(docker_init, "arl_update")
    @mock.patch.object(docker_init, "conn_db")
    def test_creates_scrypt_administrator(self, conn_db, arl_update):
        users = conn_db.return_value
        users.find_one.return_value = None

        with mock.patch.dict(os.environ, {
            "ARL_ADMIN_USERNAME": "compose-admin",
            "ARL_ADMIN_PASSWORD": "compose-secret",
        }, clear=False):
            docker_init.main()

        users.create_index.assert_called_once_with("username", unique=True)
        document = users.insert_one.call_args.args[0]
        self.assertEqual(document["username"], "compose-admin")
        self.assertTrue(check_password_hash(
            document["password_hash"], "compose-secret"
        ))
        self.assertNotIn("password", document)
        arl_update.assert_called_once_with()

    @mock.patch.object(docker_init, "arl_update")
    @mock.patch.object(docker_init, "conn_db")
    def test_existing_administrator_is_not_overwritten(self, conn_db, arl_update):
        users = conn_db.return_value
        users.find_one.return_value = {"username": "admin"}

        docker_init.main()

        users.insert_one.assert_not_called()
        arl_update.assert_called_once_with()

    @mock.patch.object(docker_init, "conn_db")
    def test_rejects_empty_credentials(self, conn_db):
        with mock.patch.dict(os.environ, {
            "ARL_ADMIN_USERNAME": "",
            "ARL_ADMIN_PASSWORD": "secret",
        }, clear=False):
            with self.assertRaises(SystemExit):
                docker_init.main()

        conn_db.assert_not_called()


if __name__ == "__main__":
    unittest.main()
