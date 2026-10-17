"""Opt-in real Compose lifecycle test; never deletes a volume or canonical graph."""

from pathlib import Path
import subprocess
from uuid import uuid4

import httpx
import pytest

from app.graph.connection import connect

pytestmark = [pytest.mark.integration, pytest.mark.persistence]
ROOT = Path(__file__).resolve().parents[3]


def compose(*args):
    completed = subprocess.run(
        ["docker", "compose", "--project-directory", str(ROOT), "-f", str(ROOT / "compose.yaml"), *args],
        cwd=ROOT, capture_output=True, text=True, timeout=150,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return completed.stdout.strip()


def test_graph_survives_restart_and_recreation(settings, graph):
    # Preflight verifies the lifecycle target before any restart.
    container = compose("ps", "-q", "falkordb")
    assert container and "\n" not in container
    graph.query("CREATE (:B01Probe {id:$id, value:$value})",
                params={"id": "PERSISTENCE", "value": "SYNTHETIC-B01"}, timeout=1000)
    name = graph.name
    marker = "b01-" + uuid4().hex
    browser_path = f"/var/lib/falkordb/browser/.data/{marker}"
    compose("exec", "-T", "falkordb", "node", "-e",
            f"require('fs').writeFileSync('{browser_path}', 'SYNTHETIC-B01')")

    def verify(stage):
        # Fresh process connection, not an in-memory cached query result.
        with connect(settings) as client:
            result = client.select_graph(name).ro_query(
                "MATCH (n:B01Probe {id:$id}) RETURN n.value LIMIT 1",
                params={"id": "PERSISTENCE"}, timeout=1000,
            )
            assert result.result_set == [["SYNTHETIC-B01"]]
            assert client.connection.config_get("dir")["dir"] == "/var/lib/falkordb/data"
            assert client.connection.config_get("appendonly")["appendonly"] == "yes"
            assert client.connection.config_get("appendfsync")["appendfsync"] == "always"
        assert httpx.get(f"http://127.0.0.1:{settings.browser_port}", follow_redirects=True, timeout=10).status_code == 200
        persisted = compose("exec", "-T", "falkordb", "node", "-e",
                            f"process.stdout.write(require('fs').readFileSync('{browser_path}', 'utf8'))")
        assert persisted == "SYNTHETIC-B01"
        print(f"{stage}: graph={name}; node=PERSISTENCE; fresh MATCH PASS; Browser HTTP 200; Browser volume PASS")

    try:
        verify("before restart")
        compose("restart", "falkordb")
        compose("up", "-d", "--wait", "--wait-timeout", "120", "falkordb")
        assert compose("ps", "-q", "falkordb") == container
        verify("after restart (same container)")
        compose("up", "-d", "--force-recreate", "--wait", "--wait-timeout", "120", "falkordb")
        replacement = compose("ps", "-q", "falkordb")
        assert replacement and replacement != container
        verify("after recreation (different container, retained volume)")
    finally:
        compose("exec", "-T", "falkordb", "node", "-e",
                f"require('fs').rmSync('{browser_path}', {{force:true}})")
