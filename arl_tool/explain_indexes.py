"""Print execution plans for ARL's representative paginated queries.

Run this against an initialized deployment after adding realistic data::

    python -m arl_tool.explain_indexes
"""

import json

from app.utils.conn import conn_db


CASES = {
    "task_by_status": ("task", {"status": "done"}, [("_id", -1)]),
    "domain_by_task": ("domain", {"task_id": "explain-placeholder"}, [("_id", -1)]),
    "site_by_task": ("site", {"task_id": "explain-placeholder"}, [("_id", -1)]),
    "asset_site_by_scope": ("asset_site", {"scope_id": "explain-placeholder"}, [("_id", -1)]),
    "schedule_by_status": ("task_schedule", {"status": "scheduled"}, [("_id", -1)]),
    "github_result_by_task": (
        "github_result", {"github_task_id": "explain-placeholder"}, [("_id", -1)]
    ),
}


def explain_cases():
    plans = {}
    for name, (collection, query, order) in CASES.items():
        plans[name] = conn_db(collection).find(query).sort(order).limit(20).explain()
    return plans


def uses_index(value):
    if isinstance(value, dict):
        if value.get("stage") in {"IXSCAN", "COUNT_SCAN", "DISTINCT_SCAN"}:
            return True
        return any(uses_index(item) for item in value.values())
    if isinstance(value, list):
        return any(uses_index(item) for item in value)
    return False


def main():
    failures = []
    for name, plan in explain_cases().items():
        stats = plan.get("executionStats", {})
        planner = plan.get("queryPlanner", {})
        indexed = uses_index(planner.get("winningPlan", {}))
        print(json.dumps({
            "case": name,
            "namespace": planner.get("namespace"),
            "winning_plan": planner.get("winningPlan"),
            "returned": stats.get("nReturned"),
            "docs_examined": stats.get("totalDocsExamined"),
            "keys_examined": stats.get("totalKeysExamined"),
            "uses_index": indexed,
        }, ensure_ascii=False, default=str))
        if not indexed:
            failures.append(name)
    if failures:
        raise SystemExit("queries without IXSCAN: {}".format(", ".join(failures)))


if __name__ == "__main__":
    main()
