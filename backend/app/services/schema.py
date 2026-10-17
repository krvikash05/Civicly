"""Local schema administration only; not an agent or business-write tool."""

from app.config import Settings
from app.graph.connection import connect
from app.graph.migration import MigrationRunner


def schema_operation(settings: Settings, *, apply: bool, retry_failed: bool = False) -> dict:
    with connect(settings) as client:
        runner = MigrationRunner(client, settings.graph)
        return runner.apply(retry_failed=retry_failed) if apply else runner.status()
