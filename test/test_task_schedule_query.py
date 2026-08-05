import unittest
from unittest.mock import patch

from app.routes.task_schedule import ARLTaskScheduleResult


class TestTaskScheduleQuery(unittest.TestCase):
    def test_legacy_schedule_status_filters_persisted_status(self):
        resource = ARLTaskScheduleResult()
        with patch.object(resource.parser, "parse_args", return_value={
            "page": 1, "size": 20, "schedule_status": "stop"
        }), patch.object(resource, "build_data", return_value={"items": []}) as build_data:
            ARLTaskScheduleResult.get.__wrapped__(resource)

        args = build_data.call_args.kwargs["args"]
        self.assertNotIn("schedule_status", args)
        self.assertEqual(args["status"], "stop")


if __name__ == "__main__":
    unittest.main()
