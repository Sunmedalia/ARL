import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.config import Config
from app.services.ai import store
from app.services.ai.chat import AIChatService, bounded_context, context_size
from app.services.ai.tools import execute_tool, validate_task_options


class _Indexes:
    def __init__(self):
        self.calls = []

    def create_index(self, *args, **kwargs):
        self.calls.append((args, kwargs))


class _TextChat(AIChatService):
    def _history(self, conversation_id):
        return []


class TestAISecurity(unittest.TestCase):
    def test_sensitive_audit_fields_are_redacted(self):
        value = store.redact({"query": "ok", "nested": {"api_key": "secret", "Token": "x"}})
        self.assertEqual(value["nested"]["api_key"], "[REDACTED]")
        self.assertEqual(value["nested"]["Token"], "[REDACTED]")

    def test_ai_collections_have_ttl_indexes(self):
        collections = {}

        def fake_conn(name):
            return collections.setdefault(name, _Indexes())

        with patch("app.services.ai.store.conn_db", side_effect=fake_conn):
            store.ensure_ai_indexes()
        for name in store.AI_COLLECTIONS:
            self.assertTrue(any(call[0] == ("expires_at",) and call[1].get("expireAfterSeconds") == 0
                                for call in collections[name].calls))

    def test_task_creation_requires_grant(self):
        with self.assertRaises(PermissionError):
            execute_tool("create_asset_discovery_task", {
                "name": "test", "target": "example.com", "options": {}
            }, can_create=False)

    def test_scan_option_validation_rejects_invalid_ports_and_types(self):
        with self.assertRaises(ValueError):
            validate_task_options({"port_scan_type": "custom", "port_custom": "80,70000"})
        with self.assertRaises(ValueError):
            validate_task_options({"nuclei_scan": "yes"})
        with self.assertRaises(ValueError):
            validate_task_options({"unknown": True})

    def test_text_stream_has_stable_events(self):
        delta = SimpleNamespace(content="资产正常", tool_calls=[])
        chunk = SimpleNamespace(choices=[SimpleNamespace(delta=delta)])
        completions = SimpleNamespace(create=lambda **kwargs: iter([chunk]))
        client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
        service = _TextChat(client=client)
        with patch("app.services.ai.chat.store.add_message"):
            events = list(service.stream("conversation", "admin", "session", "状态"))
        self.assertEqual([item["event"] for item in events],
                         ["message_start", "text_delta", "done"])
        self.assertEqual(events[1]["data"]["text"], "资产正常")

    def test_fragmented_tool_arguments_and_multiple_rounds(self):
        tool_a = SimpleNamespace(index=0, id="call-1", function=SimpleNamespace(
            name="list_tasks", arguments='{"sta'))
        tool_b = SimpleNamespace(index=0, id=None, function=SimpleNamespace(
            name=None, arguments='tus":"error"}'))
        first = [
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=None, tool_calls=[tool_a]))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=None, tool_calls=[tool_b]))]),
        ]
        second = [SimpleNamespace(choices=[SimpleNamespace(
            delta=SimpleNamespace(content="发现 1 个失败任务", tool_calls=[])
        )])]
        streams = iter([iter(first), iter(second)])
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
            create=lambda **kwargs: next(streams)
        )))
        service = _TextChat(client=client)
        with patch("app.services.ai.chat.store.add_message"), \
                patch("app.services.ai.chat.store.grant_exists", return_value=False), \
                patch("app.services.ai.chat.store.audit_action"), \
                patch("app.services.ai.chat.execute_tool", return_value={"items": [{"status": "error"}]}):
            events = list(service.stream("conversation", "admin", "session", "失败任务"))
        names = [event["event"] for event in events]
        self.assertEqual(names.count("tool_start"), 1)
        self.assertEqual(names.count("tool_result"), 1)
        self.assertIn("text_delta", names)
        self.assertEqual(names[-1], "done")

    def test_model_failure_isolated_as_error_event(self):
        def fail(**kwargs):
            raise TimeoutError("secret upstream detail")
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
        service = _TextChat(client=client)
        with patch("app.services.ai.chat.store.add_message"), \
                patch("app.services.ai.chat.logger.exception") as log_exception:
            events = list(service.stream("conversation", "admin", "session", "状态"))
        self.assertEqual(events[-1]["event"], "error")
        self.assertEqual(events[-1]["data"]["error_code"], "MODEL_CALL_FAILED")
        self.assertNotIn("secret", events[-1]["data"]["message"])
        log_exception.assert_called_once()

    def test_context_budget_keeps_system_latest_user_and_recent_tool_result(self):
        messages = [
            {"role": "system", "content": "system"},
            {"role": "assistant", "content": "old" * 1000},
            {"role": "user", "content": "latest question"},
            {"role": "assistant", "content": None, "tool_calls": [{
                "id": "call-1", "type": "function",
                "function": {"name": "list_tasks", "arguments": "{}"},
            }]},
            {"role": "tool", "tool_call_id": "call-1", "content": "recent result" * 1000},
        ]
        bounded = bounded_context(messages, budget=900)
        self.assertLessEqual(context_size(bounded), 900)
        self.assertEqual(bounded[0]["role"], "system")
        self.assertTrue(any(item.get("content") == "latest question" for item in bounded))
        self.assertTrue(any(item.get("role") == "tool" for item in bounded))
        self.assertFalse(any(item.get("content") == "old" * 1000 for item in bounded))

    def test_tool_exception_is_logged_but_not_returned_to_client(self):
        tool_call = SimpleNamespace(index=0, id="call-1", function=SimpleNamespace(
            name="list_tasks", arguments="{}"
        ))
        first = [SimpleNamespace(choices=[SimpleNamespace(
            delta=SimpleNamespace(content=None, tool_calls=[tool_call])
        )])]
        second = [SimpleNamespace(choices=[SimpleNamespace(
            delta=SimpleNamespace(content="done", tool_calls=[])
        )])]
        streams = iter([iter(first), iter(second)])
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
            create=lambda **kwargs: next(streams)
        )))
        service = _TextChat(client=client)
        with patch("app.services.ai.chat.store.add_message"), \
                patch("app.services.ai.chat.store.grant_exists", return_value=False), \
                patch("app.services.ai.chat.store.audit_action"), \
                patch("app.services.ai.chat.execute_tool", side_effect=RuntimeError("db password leaked")), \
                patch("app.services.ai.chat.logger.exception") as log_exception:
            events = list(service.stream("conversation", "admin", "session", "status"))
        result = next(item["data"]["result"] for item in events if item["event"] == "tool_result")
        self.assertEqual(result["error_code"], "TOOL_EXECUTION_FAILED")
        self.assertNotIn("password", str(result))
        log_exception.assert_called_once()


if __name__ == "__main__":
    unittest.main()
