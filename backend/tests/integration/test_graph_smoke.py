import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from redis.exceptions import ResponseError

from app.services.health import check_health

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[3]
CLI = Path(sys.executable).with_name("civicly")


def test_parameterized_create_match(graph, settings):
    # Includes text which must remain a value, never executable Cypher.
    value = 'synthetic "quoted" \\ text; MATCH (n) DELETE n'
    created = graph.query(
        "CREATE (n:B01Probe {id:$id, value:$value}) RETURN n.id, n.value",
        params={"id": "B01-CREATE", "value": value}, timeout=settings.query_timeout_ms,
    )
    assert created.result_set == [["B01-CREATE", value]]
    matched = graph.ro_query(
        "MATCH (n:B01Probe {id:$id}) RETURN n.id, n.value LIMIT 1",
        params={"id": "B01-CREATE"}, timeout=settings.query_timeout_ms,
    )
    assert matched.result_set == created.result_set


def test_readonly_rejects_create_set_delete_without_mutation(graph, settings):
    graph.query("CREATE (:B01Probe {id:$id, value:$value})",
                params={"id": "ORIGINAL", "value": "unchanged"}, timeout=settings.query_timeout_ms)
    for query in (
        "CREATE (:B01Probe {id:$id})",
        "MATCH (n:B01Probe {id:$id}) SET n.value='changed'",
        "MATCH (n:B01Probe {id:$id}) DELETE n",
    ):
        with pytest.raises(ResponseError, match="read.only") as error:
            graph.ro_query(query, params={"id": "ORIGINAL"}, timeout=settings.query_timeout_ms)
        print("Expected server denial:", error.value)
    assert graph.ro_query("MATCH (n:B01Probe) RETURN n.id, n.value LIMIT 10").result_set == [
        ["ORIGINAL", "unchanged"]
    ]


def test_foundation_health_uses_graph_read_without_mutation(db, graph, settings):
    graph.query("CREATE (:B01Probe {id:$id})", params={"id": "HEALTH"}, timeout=1000)
    before = set(db.list_graphs())
    result = check_health(settings.model_copy(update={"graph": graph.name}))
    assert result.status == "ok", result.model_dump()
    assert result.graph_state == "available"
    assert result.checks == {"redis_ping": True, "graph_module": True, "graph_read": True}
    assert set(db.list_graphs()) == before


def test_foundation_health_reports_uninitialized_without_writing(db, settings):
    from uuid import uuid4
    name = "civicly_b01_missing_" + uuid4().hex
    before = set(db.list_graphs())
    result = check_health(settings.model_copy(update={"graph": name}))
    assert result.status == "ok"
    assert result.graph_state == "uninitialized"
    assert result.checks["graph_read"] is None
    assert set(db.list_graphs()) == before


def test_cli_health_success(settings):
    result = subprocess.run([str(CLI), "health"], cwd=ROOT, capture_output=True, text=True, timeout=15)
    assert result.returncode == 0, result.stdout + result.stderr
    body = json.loads(result.stdout)
    assert body["status"] == "ok"
    assert body["scope"] == "backend_foundation"


def test_cli_graph_unavailable_fails_and_redacts():
    result = subprocess.run(
        [str(CLI), "health", "--env-file", "/dev/null"], cwd=ROOT,
        env={**os.environ, "FALKORDB_PORT": "1", "FALKORDB_PASSWORD": "PRIVATE-PROBE"},
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout)["error_code"] == "GRAPH_UNAVAILABLE"
    assert "PRIVATE-PROBE" not in result.stdout + result.stderr
