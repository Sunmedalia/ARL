import sys
import os
import threading
from . import conn_db
from app.config import Config


def update_task_tag():
    """更新task任务tag信息"""
    table = "task"
    items = conn_db(table).find({})
    for item in items:
        task_tag = item.get("task_tag")
        query = {"_id": item["_id"]}
        if not task_tag:
            item["task_tag"] = "task"
            conn_db(table).find_one_and_replace(query, item)


QUERY_INDEXES = {
    "task": [
        [("status", 1), ("_id", -1)],
        [("task_tag", 1), ("_id", -1)],
        [("start_time", -1), ("_id", -1)],
    ],
    "domain": [
        [("task_id", 1), ("_id", -1)], [("task_id", 1), ("domain", 1)], [("domain", 1)],
    ],
    "ip": [[("task_id", 1), ("_id", -1)]],
    "site": [
        [("task_id", 1), ("_id", -1)], [("task_id", 1), ("site", 1)],
        [("status", 1)], [("title", 1)], [("hostname", 1)], [("site", 1)],
        [("http_server", 1)],
    ],
    "service": [[("task_id", 1), ("_id", -1)]],
    "url": [[("task_id", 1), ("_id", -1)]],
    "vuln": [[("task_id", 1), ("_id", -1)]],
    "nuclei_result": [[("task_id", 1), ("_id", -1)]],
    "fileleak": [[("task_id", 1), ("_id", -1)]],
    "wih": [
        [("task_id", 1), ("_id", -1)], [("task_id", 1), ("record_type", 1)],
        [("record_type", 1)], [("fnv_hash", 1)],
    ],
    "cert": [[("task_id", 1), ("_id", -1)]],
    "cip": [[("task_id", 1), ("_id", -1)]],
    "npoc_service": [[("task_id", 1), ("_id", -1)]],
    "asset_domain": [
        [("scope_id", 1), ("_id", -1)], [("scope_id", 1), ("domain", 1)],
        [("domain", 1)],
    ],
    "asset_ip": [[("scope_id", 1), ("_id", -1)]],
    "asset_site": [[("scope_id", 1), ("_id", -1)], [("scope_id", 1), ("site", 1)]],
    "asset_wih": [[("scope_id", 1), ("_id", -1)]],
    "scheduler": [
        [("status", 1), ("_id", -1)], [("scope_id", 1), ("_id", -1)],
        [("next_run_time", 1), ("_id", -1)],
    ],
    "task_schedule": [
        [("status", 1), ("_id", -1)], [("next_run_date", 1), ("_id", -1)],
    ],
    "github_task": [[("status", 1), ("_id", -1)]],
    "github_scheduler": [
        [("status", 1), ("_id", -1)], [("next_run_date", 1), ("_id", -1)],
    ],
    "github_result": [[("github_task_id", 1), ("_id", -1)]],
    "github_monitor_result": [[("github_scheduler_id", 1), ("_id", -1)]],
}


def ensure_query_indexes():
    """Create indexes used by paginated task, scope, status and time queries."""
    for collection, indexes in QUERY_INDEXES.items():
        for index in indexes:
            conn_db(collection).create_index(index)


def create_index():
    """Backward-compatible entry point for existing maintenance scripts."""
    ensure_query_indexes()


def arl_update():
    if is_run_flask_routes():
        return

    # TTL/security indexes are idempotent and must not be skipped by the
    # historical one-time update lock when upgrading an existing deployment.
    from app.auth_session import ensure_auth_indexes
    from app.services.ai.store import ensure_ai_indexes
    ensure_auth_indexes()
    ensure_ai_indexes()
    ensure_query_indexes()

    npoc_info_update()

    update_lock = os.path.join(Config.TMP_PATH, 'arl_update.lock')
    if os.path.exists(update_lock):
        return

    update_task_tag()
    open(update_lock, 'a').close()


# 创建锁，防止多线程同时更新
lock = threading.Lock()


def npoc_info_update():
    from app.services.npoc import NPoC
    with lock:
        if conn_db('poc').count_documents({}) > 0:
            return

        n = NPoC()
        n.sync_to_db()


# 判断是否是-m flask routes 模式运行
def is_run_flask_routes():
    if len(sys.argv) == 2:
        if "flask/__main__.py" in sys.argv[0]:
            if sys.argv[1] == "routes":
                return True

    return False
