"""Foundation health, deliberately not full agent-system readiness."""

from typing import Literal

from pydantic import BaseModel
from redis.exceptions import RedisError

from app.config import Settings
from app.graph.connection import connect


class FoundationHealth(BaseModel):
    scope: Literal["backend_foundation"] = "backend_foundation"
    status: Literal["ok", "unavailable"]
    graph: str
    graph_state: Literal["uninitialized", "available", "unavailable"]
    checks: dict[str, bool | None]
    error_code: str | None = None


def check_health(settings: Settings) -> FoundationHealth:
    checks: dict[str, bool | None] = {
        "redis_ping": False, "graph_module": False, "graph_read": None,
    }
    graph_state = "uninitialized"
    try:
        with connect(settings) as client:
            checks["redis_ping"] = client.connection.ping() is True
            checks["graph_module"] = any(
                module["name"] == "graph" for module in client.connection.module_list()
            )
            if settings.graph in client.list_graphs():
                graph_state = "available"
                result = client.select_graph(settings.graph).ro_query(
                    "RETURN $probe AS probe LIMIT 1",
                    params={"probe": "civicly-health"},
                    timeout=settings.query_timeout_ms,
                )
                checks["graph_read"] = result.result_set == [["civicly-health"]]
    except RedisError:
        # Do not print library exceptions: they may contain connection credentials.
        return FoundationHealth(
            status="unavailable", graph=settings.graph, graph_state="unavailable", checks=checks,
            error_code="GRAPH_UNAVAILABLE",
        )
    healthy = checks["redis_ping"] and checks["graph_module"] and checks["graph_read"] is not False
    return FoundationHealth(
        status="ok" if healthy else "unavailable",
        graph=settings.graph, graph_state=graph_state if healthy else "unavailable", checks=checks,
        error_code=None if healthy else "GRAPH_HEALTH_INVALID",
    )
