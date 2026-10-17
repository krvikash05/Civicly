"""Additive, checksummed schema migration with real operational readiness."""

import hashlib
import json
from pathlib import Path
import re
import time

from redis.exceptions import LockNotOwnedError

from app.graph.schema import Registry, identifier, utc_now

PLAN_PATH = Path(__file__).with_name("migrations") / "0001.json"
META = "CivicSchemaMigration"


class MigrationError(RuntimeError):
    pass


class MigrationRunner:
    def __init__(self, client, graph_name: str, registry: Registry | None = None):
        if graph_name != "civicly_knowledge" and not re.fullmatch(r"civicly_b02_test_[0-9a-f]{32}", graph_name):
            raise MigrationError("Migration target must be canonical or an isolated B02 test graph")
        self.client = client
        self.graph = client.select_graph(graph_name)
        self.registry = registry or Registry()
        raw = PLAN_PATH.read_bytes()
        self.checksum = hashlib.sha256(raw).hexdigest()
        self.plan = json.loads(raw)
        if self.plan["registry_sha256"] != self.registry.sha256:
            raise MigrationError("Registry differs from immutable migration; add a new migration")
        self.lock = client.connection.lock(f"civicly:schema-lock:{graph_name}", timeout=60, blocking=False)

    def _catalog(self, procedure: str) -> list[dict]:
        # Only fixed built-in procedure names, not arbitrary caller Cypher.
        if procedure not in {"indexes", "constraints"}:
            raise MigrationError("Unknown catalog")
        fields = "label,properties,types,entitytype,status" if procedure == "indexes" else "type,label,properties,entitytype,status"
        result = self.graph.ro_query(f"CALL db.{procedure}() YIELD {fields} RETURN {fields} LIMIT 513", timeout=1000)
        if len(result.result_set) > 512:
            raise MigrationError("Schema catalog exceeds bounded migration budget")
        columns = [column[1] for column in result.header]
        return [dict(zip(columns, row, strict=True)) for row in result.result_set]

    def _rows(self, kind: str, spec: dict) -> list[dict]:
        return [row for row in self._catalog(kind)
                if row["label"] == spec["label"] and row["entitytype"] == spec["entity"]]

    def _wait(self, kind: str, spec: dict, seconds: float = 5) -> None:
        deadline = time.monotonic() + seconds
        while True:
            rows = self._rows(kind, spec)
            if kind == "constraints":
                rows = [r for r in rows if r["type"] == spec["type"] and
                        sorted(r["properties"]) == sorted(spec["properties"])]
            else:
                rows = [r for r in rows if set(spec["properties"]).issubset(r["properties"]) and
                        all("RANGE" in r["types"].get(p, []) for p in spec["properties"])]
            if any(row["status"] == "FAILED" for row in rows):
                raise MigrationError(f"FAILED {kind} for {spec['label']}; repair data before explicit retry")
            if rows and all(row["status"] == "OPERATIONAL" for row in rows):
                return
            if time.monotonic() >= deadline:
                raise MigrationError(f"Readiness timeout: {kind} {spec['label']}")
            time.sleep(0.02)

    def _ensure_index(self, spec: dict) -> None:
        label = identifier(spec["label"])
        rows = self._rows("indexes", spec)
        existing = {p for row in rows for p in row["properties"] if "RANGE" in row["types"].get(p, [])}
        missing = [identifier(p) for p in spec["properties"] if p not in existing]
        if missing:
            pattern = f"(n:{label})" if spec["entity"] == "NODE" else f"()-[n:{label}]-()"
            fields = ",".join(f"n.{p}" for p in missing)
            self.graph.query(f"CREATE INDEX FOR {pattern} ON ({fields})", timeout=1000)
        self._wait("indexes", spec)

    def _ensure_constraint(self, spec: dict, retry_failed: bool) -> None:
        rows = [r for r in self._rows("constraints", spec) if r["type"] == spec["type"] and
                sorted(r["properties"]) == sorted(spec["properties"])]
        if rows and rows[0]["status"] == "FAILED" and retry_failed:
            self._constraint_command("DROP", spec)
            rows = []
        if not rows:
            self._constraint_command("CREATE", spec)
        self._wait("constraints", spec)

    def _constraint_command(self, operation: str, spec: dict):
        # Command arguments are separate; no property values or AI Cypher involved.
        return self.client.execute_command(
            "GRAPH.CONSTRAINT", operation, self.graph.name, spec["type"],
            spec["entity"], identifier(spec["label"]), "PROPERTIES", len(spec["properties"]),
            *(identifier(p) for p in spec["properties"]),
        )

    def _history(self) -> list[dict]:
        if self.graph.name not in self.client.list_graphs():
            return []
        result = self.graph.ro_query(
            f"MATCH (m:{META}) RETURN properties(m) LIMIT 101", timeout=1000,
        ).result_set
        if len(result) > 100:
            raise MigrationError("Migration history exceeds budget")
        return [row[0] for row in result]

    def _verify_history(self):
        history = self._history()
        if len(history) > 1:
            raise MigrationError("Unexpected migration history; forward version unsupported")
        for entry in history:
            if entry.get("state") not in {"APPLYING", "FAILED", "READY"}:
                raise MigrationError("Unknown migration state; no mutation permitted")
            if entry.get("version") != self.plan["version"] or entry.get("id") != self.plan["id"]:
                raise MigrationError("Unknown migration version; no downgrade permitted")
            if entry.get("checksum") != self.checksum or entry.get("registry_sha256") != self.registry.sha256:
                raise MigrationError("Applied migration checksum mismatch; no mutation permitted")
        return history

    def _record(self, state: str, *, attempt: bool = False, error: str = ""):
        existing = self._history()
        events = json.loads(existing[0].get("state_history", "[]")) if existing else []
        if len(events) >= 1000:
            raise MigrationError("Migration audit capacity reached; review before further retries")
        now = utc_now()
        events.append({"state": state, "at": now, "error_code": error})
        self.graph.query(
            f"MERGE (m:{META} {{id:$id}}) "
            "ON CREATE SET m.started_at=$now, m.attempts=0 "
            "SET m.version=$version,m.checksum=$checksum,m.registry_sha256=$registry,"
            "m.state=$state,m.updated_at=$now,m.error_code=$error,m.attempts=m.attempts+$attempt,"
            "m.state_history=$events "
            "RETURN m.id LIMIT 1",
            params={"id": self.plan["id"], "now": now, "version": self.plan["version"],
                    "checksum": self.checksum, "registry": self.registry.sha256, "state": state,
                    "error": error, "attempt": int(attempt), "events": json.dumps(events)}, timeout=1000,
        )

    def status(self) -> dict:
        history = self._verify_history()
        issues = []
        if not history or history[0].get("state") != "READY":
            issues.append("Migration not recorded READY")
        if self.graph.name in self.client.list_graphs():
            for kind in ("indexes", "constraints"):
                actual = self._catalog(kind)
                for spec in self.plan[kind]:
                    rows = [r for r in actual if r["label"] == spec["label"] and r["entitytype"] == spec["entity"]]
                    if kind == "constraints":
                        rows = [r for r in rows if r["type"] == spec["type"] and
                                sorted(r["properties"]) == sorted(spec["properties"])]
                    else:
                        rows = [r for r in rows if set(spec["properties"]).issubset(r["properties"]) and
                                all("RANGE" in r["types"].get(p, []) for p in spec["properties"])]
                    if not rows or any(r["status"] != "OPERATIONAL" for r in rows):
                        issues.append(f"{kind}:{spec['label']}:{spec.get('type', 'RANGE')} unavailable")
        else:
            issues.append("Canonical graph absent")
        return {"graph": self.graph.name, "migration_version": self.plan["version"] if history else 0,
                "registry_version": self.registry.version, "municipality_id": self.registry.scope,
                "ready": not issues, "index_groups": len(self.plan["indexes"]),
                "constraints": len(self.plan["constraints"]), "issues": issues,
                "history": history}

    def apply(self, *, retry_failed: bool = False) -> dict:
        if not self.lock.acquire(blocking=False):
            raise MigrationError("Another migration holds the schema lease")
        recorded = False
        try:
            self._verify_history()  # Must happen before any mutation, even bootstrap.
            # Schema commands themselves create an empty graph; no fake domain node.
            bootstrap = self.plan["indexes"][0]
            if self.graph.name not in self.client.list_graphs():
                self.graph.query(f"CREATE INDEX FOR (n:{META}) ON (n.id)", timeout=1000)
            self._ensure_index(bootstrap)
            for spec in self.plan["constraints"][:2]:
                self._ensure_constraint(spec, retry_failed)
            self._record("APPLYING", attempt=True)
            recorded = True
            for spec in self.plan["indexes"]:
                self.lock.extend(60, replace_ttl=True)
                self._ensure_index(spec)
            for spec in self.plan["constraints"]:
                self.lock.extend(60, replace_ttl=True)
                self._ensure_constraint(spec, retry_failed)
            self._record("READY")
            result = self.status()
            if not result["ready"]:
                raise MigrationError("Final schema readiness verification failed")
            return result
        except Exception:
            if recorded and self.lock.owned():
                self._record("FAILED", error="SCHEMA_MIGRATION_FAILED")
            raise
        finally:
            try:
                self.lock.release()
            except LockNotOwnedError:
                pass
