"""Canonical integrity repositories. Only trusted future domain services may write."""

from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass
import json
from pathlib import Path
from uuid import uuid4

from redis.exceptions import LockNotOwnedError, RedisError

from app.graph.targets import is_allowed_graph_target
from app.graph.migration import MigrationRunner
from app.graph.models import EdgeRecord, NodeRecord, digest
from app.graph.schema import Registry, SchemaError, timestamp, utc_now

POLICY_PATH = Path(__file__).resolve().parents[3] / "contracts/graph_access.json"


class RepositoryError(RuntimeError):
    code = "GRAPH_INTEGRITY_ERROR"


class NotFound(RepositoryError):
    code = "NOT_FOUND"


class Conflict(RepositoryError):
    code = "CONFLICT"


class PreconditionFailed(RepositoryError):
    code = "PRECONDITION_FAILED"


class ScopeError(RepositoryError):
    code = "INVALID_SCOPE"


class OutcomeUnknown(RepositoryError):
    code = "WRITE_OUTCOME_UNKNOWN"


@dataclass
class WriteSession:
    owner: str
    epoch: int
    revision: int
    audit: list


def interval(props: dict):
    return (timestamp(props["valid_from"]) if "valid_from" in props else None,
            timestamp(props["valid_to"]) if "valid_to" in props else None)


def intersection(a, b):
    lower = max(x for x in (a[0], b[0]) if x is not None) if any(x is not None for x in (a[0], b[0])) else None
    upper = min(x for x in (a[1], b[1]) if x is not None) if any(x is not None for x in (a[1], b[1])) else None
    return None if lower is not None and upper is not None and lower >= upper else (lower, upper)


class GraphRepository:
    def __init__(self, client, graph_name="civicly_knowledge", *, lease_seconds=10):
        if not is_allowed_graph_target(graph_name):
            raise PreconditionFailed("Repository target must be canonical or an authorized disposable test graph")
        if not 0.1 <= lease_seconds <= 60:
            raise ValueError("Invalid writer lease duration")
        self.client, self.graph = client, client.select_graph(graph_name)
        self.registry = Registry()
        self.policy = json.loads(POLICY_PATH.read_text())
        if not MigrationRunner(client, graph_name).status()["ready"]:
            raise PreconditionFailed("Canonical migration is not operational")
        self.lease_seconds = lease_seconds

    def _read(self, query, params=None):
        return self.graph.ro_query(query, params=params, timeout=1000).result_set

    def decode_node(self, labels, properties) -> NodeRecord:
        props = dict(properties)
        if props.get("municipality_id") != self.registry.scope:
            raise ScopeError("Node municipality is invalid")
        public = set(labels) - {self.registry.base_label}
        primary = [label for label in public if label in self.registry.nodes and
                   not any(label in self.registry.nodes.get(other, {}).get("labels", []) for other in public)]
        if len(primary) != 1 or set(labels) != set(self.registry.labels(primary[0])):
            raise RepositoryError("Node has incompatible canonical labels")
        self.registry.validate_node(primary[0], props)
        return NodeRecord(id=props["id"], kind=primary[0], labels=tuple(sorted(public)), properties=props)

    def _node_optional(self, id) -> NodeRecord | None:
        if not isinstance(id, str) or not id.strip():
            raise SchemaError("Invalid application ID")
        rows = self._read("MATCH (n:CivicEntity {id:$id}) RETURN labels(n),properties(n) LIMIT 2", {"id": id})
        if len(rows) > 1:
            raise Conflict("Duplicate global node ID detected")
        return self.decode_node(*rows[0]) if rows else None

    def get_node(self, id: str, expected_kind: str | None = None) -> NodeRecord:
        node = self._node_optional(id)
        if node is None:
            raise NotFound("Canonical node does not exist")
        if expected_kind is not None:
            self.registry.shape(expected_kind)
            if expected_kind not in node.labels:
                raise PreconditionFailed("Node has incompatible type")
        return node

    def _decode_edge_row(self, row) -> EdgeRecord:
        kind, props, sl, sp, tl, tp = row
        source, target = self.decode_node(sl, sp), self.decode_node(tl, tp)
        self.registry.validate_edge(kind, source.kind, source.properties, target.kind, target.properties, dict(props))
        return EdgeRecord(id=props["id"], kind=kind, source=source.id, target=target.id, properties=dict(props))

    def _edge_optional(self, id) -> EdgeRecord | None:
        if not isinstance(id, str) or not id.strip():
            raise SchemaError("Invalid relationship ID")
        rows = self._read(
            "MATCH (s)-[r]->(t) WHERE r.id=$id "
            "RETURN type(r),properties(r),labels(s),properties(s),labels(t),properties(t) LIMIT 2", {"id": id})
        if len(rows) > 1:
            raise Conflict("Relationship ID reused across types")
        return self._decode_edge_row(rows[0]) if rows else None

    def get_relationship(self, id: str) -> EdgeRecord:
        edge = self._edge_optional(id)
        if edge is None:
            raise NotFound("Relationship does not exist")
        return edge

    def _edges(self, kind, *, exclude=None) -> list[EdgeRecord]:
        if kind not in self.registry.edges:
            raise SchemaError("Unknown relationship type")
        rows = self._read(
            f"MATCH (s)-[r:{kind}]->(t) RETURN type(r),properties(r),labels(s),properties(s),"
            "labels(t),properties(t) LIMIT $limit", {"limit": self.policy["budgets"]["policy_edges"] + 1})
        if len(rows) > self.policy["budgets"]["policy_edges"]:
            raise PreconditionFailed("Policy graph exceeds safe inspection budget")
        return [edge for row in rows if (edge := self._decode_edge_row(row)).id != exclude]

    def _guard_params(self, session):
        return {"migration": "0001", "owner": session.owner, "epoch": session.epoch, "revision": session.revision}

    @staticmethod
    def _guard():
        return ("MATCH (g:CivicSchemaMigration {id:$migration}) "
                "WHERE g.state='READY' AND g.repo_owner=$owner AND g.repo_epoch=$epoch "
                "AND coalesce(g.repo_revision,0)=$revision WITH g ")

    def _recover(self, session, pending):
        if not pending:
            return
        intent = json.loads(pending)
        current = self._node_optional(intent["id"]) if intent["kind"] == "node" else self._edge_optional(intent["id"])
        before = current.content_hash if current else ""
        if before != intent["before_hash"]:
            raise OutcomeUnknown("Pending write differs from pre-state; operator reconciliation required")
        session.audit.append({**intent, "state": "ABORTED_UNCHANGED", "at": utc_now()})
        result = self.graph.query(self._guard() + "SET g.repo_pending='',g.repo_audit=$audit RETURN g.id",
                                  params={**self._guard_params(session), "audit": json.dumps(session.audit)}, timeout=1000)
        if not result.result_set:
            raise PreconditionFailed("Writer fence changed during recovery")

    @contextmanager
    def _session(self):
        lock = self.client.connection.lock(f"civicly:repository-lock:{self.graph.name}",
                                           timeout=self.lease_seconds, blocking_timeout=3)
        if not lock.acquire(blocking=True):
            raise PreconditionFailed("Graph writer is busy")
        try:
            owner = uuid4().hex
            rows = self.graph.query(
                "MATCH (g:CivicSchemaMigration {id:$migration}) WHERE g.state='READY' "
                "SET g.repo_epoch=coalesce(g.repo_epoch,0)+1,g.repo_owner=$owner "
                "RETURN g.repo_epoch,coalesce(g.repo_revision,0),coalesce(g.repo_pending,''),coalesce(g.repo_audit,'[]')",
                params={"migration": "0001", "owner": owner}, timeout=1000).result_set
            if len(rows) != 1:
                raise PreconditionFailed("Migration metadata missing or unavailable")
            epoch, revision, pending, audit = rows[0]
            session = WriteSession(owner, epoch, revision, json.loads(audit))
            if len(session.audit) >= self.policy["budgets"]["audit_entries"]:
                raise PreconditionFailed("Mutation audit budget reached; archive via reviewed migration")
            self._recover(session, pending)
            yield session
        finally:
            try:
                lock.release()
            except (LockNotOwnedError, RedisError):
                pass  # A successor's fence, never this finally block, authorizes writes.

    def recover_pending(self):
        with self._session() as session:
            return {"revision": session.revision, "pending": False}

    def _commit(self, session, kind, id, before_hash, body, params, return_alias):
        intent = {"request_id": uuid4().hex, "kind": kind, "id": id, "before_hash": before_hash,
                  "request_hash": digest(params), "at": utc_now()}
        prepared = self.graph.query(self._guard() + "SET g.repo_pending=$intent RETURN g.id",
                                    params={**self._guard_params(session), "intent": json.dumps(intent)}, timeout=1000)
        if not prepared.result_set:
            raise PreconditionFailed("Writer fence expired before preparation")
        audit = [*session.audit, {**intent, "state": "COMMITTED"}]
        query = (self._guard() + body +
                 f" SET g.repo_revision=$next_revision,g.repo_pending='',g.repo_audit=$audit RETURN {return_alias}.id LIMIT 1")
        try:
            result = self.graph.query(query, params={**params, **self._guard_params(session),
                                      "next_revision": session.revision + 1, "audit": json.dumps(audit)}, timeout=1000)
        except RedisError as error:
            # Never retry a possibly committed write. Pending marker/pre-state recovery is explicit.
            raise OutcomeUnknown("Mutation response failed; inspect/recover pending before retry") from error
        if result.result_set != [[id]]:
            raise PreconditionFailed("Mutation did not match current writer fence or endpoints")

    def _node_references(self, kind, props):
        for field, target_kind in self.policy["node_references"].get(kind, {}).items():
            if field in props:
                self.get_node(props[field], target_kind)

    def create_node(self, kind: str, properties: dict) -> NodeRecord:
        statement = self.registry.node_statement(kind, properties)
        with self._session() as session:
            if self._node_optional(properties["id"]) or self._edge_optional(properties["id"]):
                raise Conflict("Application ID already exists")
            self._node_references(kind, properties)
            self._commit(session, "node", properties["id"], "", statement.query.split(" RETURN n.id")[0], statement.params, "n")
        return self.get_node(properties["id"])

    def update_node(self, id: str, changes: dict, *, expected_hash: str) -> NodeRecord:
        if not isinstance(changes, dict):
            raise SchemaError("Changes must be an object")
        with self._session() as session:
            old = self.get_node(id)
            if old.content_hash != expected_hash:
                raise PreconditionFailed("Stale node content hash")
            if self.registry.nodes[old.kind]["immutable"]:
                raise PreconditionFailed("Append-only record cannot be updated")
            if set(changes).intersection({"id", "municipality_id", "schema_version", "created_at"}):
                raise PreconditionFailed("Stable identity/origin cannot be changed")
            props = {**old.properties, **changes}
            self.registry.validate_node(old.kind, props)
            if "updated_at" in props and timestamp(props["updated_at"]) < timestamp(old.properties["updated_at"]):
                raise PreconditionFailed("Update time cannot move backwards")
            self._node_references(old.kind, props)
            if old.kind == "Evidence" and changes.keys() & {"reliability", "observed_at", "recorded_at", "source_kind", "source_record_id"}:
                if self._read("MATCH ()-[r]->() WHERE r.source_evidence_id=$id AND r.association_status='VERIFIED' RETURN r.id LIMIT 1", {"id": id}):
                    raise PreconditionFailed("Referenced verified evidence requires a versioned domain correction")
            if old.kind == "ServiceSchedule" and changes.keys() & {"service_type", "valid_from", "valid_to"}:
                schedules = self._edges("HAS_SCHEDULE")
                routes = {edge.source for edge in schedules if edge.target == id}
                self._schedule_policies(schedules, routes, overrides={id: props})
            statement = self.registry.node_statement(old.kind, props)
            tail = statement.query.split(" SET n=", 1)[1].split(" RETURN n.id")[0]
            body = "MATCH (n:CivicEntity {id:$id,municipality_id:$scope}) SET n=" + tail
            self._commit(session, "node", id, old.content_hash, body,
                         {**statement.params, "id": id, "scope": self.registry.scope}, "n")
        return self.get_node(id)

    def _check_evidence(self, props, *, inspection=False):
        if "source_evidence_id" not in props:
            return
        evidence = self.get_node(props["source_evidence_id"], "Evidence")
        if props.get("association_status") == "VERIFIED" or inspection:
            ep = evidence.properties
            if ep["reliability"] != "VERIFIED" or ep["source_kind"] == "AGENT" or not ep.get("observed_at") or not ep.get("source_record_id"):
                raise PreconditionFailed("Verified relationship needs dated attributed verified evidence")
            if timestamp(ep["observed_at"]) > timestamp(props["created_at"]) or timestamp(ep["recorded_at"]) > timestamp(props["created_at"]) or timestamp(ep["created_at"]) > timestamp(props["created_at"]):
                raise PreconditionFailed("Relationship cannot cite future evidence")
            if inspection and ep["evidence_type"] != "INSPECTION_REPORT":
                raise PreconditionFailed("Drainage cycle exception requires inspection evidence")
        return evidence

    def _schedule_policies(self, edges, routes, *, overrides=None):
        """Exclusive route/service definitions over actual shared applicability."""
        schedules, groups = dict(overrides or {}), {}
        steps = 0
        for edge in edges:
            if edge.source not in routes:
                continue
            if edge.target not in schedules:
                schedules[edge.target] = self.get_node(edge.target, "ServiceSchedule").properties
            schedule = schedules[edge.target]
            active = intersection(interval(edge.properties), interval(schedule))
            if active is None:
                raise PreconditionFailed("Schedule assignment has no applicable validity interval")
            group = groups.setdefault((edge.source, schedule["service_type"]), [])
            for previous in group:
                steps += 1
                if steps > self.policy["budgets"]["policy_steps"]:
                    raise PreconditionFailed("Schedule conflict proof exceeded inspection budget")
                if intersection(active, previous) is not None:
                    raise Conflict("Overlapping route schedules for the same service")
            group.append(active)

    def _relationship_policies(self, kind, source, target, props, *, exclude=None, inspected_cycle_evidence_id=None):
        self.registry.validate_edge(kind, source.kind, source.properties, target.kind, target.properties, props)
        self._check_evidence(props)
        edges = self._edges(kind, exclude=exclude)
        span = interval(props)
        for edge in edges:
            if edge.source == source.id and intersection(span, interval(edge.properties)) is not None:
                if edge.target == target.id or kind in self.policy["singleton_outgoing"]:
                    raise Conflict("Duplicate or cardinality-conflicting active relationship")
        if kind == "HAS_SCHEDULE":
            candidate = EdgeRecord(id=props["id"], kind=kind, source=source.id, target=target.id, properties=props)
            self._schedule_policies([*edges, candidate], {source.id})
        if kind not in {*self.policy["permanent_dag"], "DRAINS_TO"}:
            return
        queue = deque([(target.id, span)])
        visited = set()
        steps = 0
        while queue:
            node, active = queue.popleft()
            key = (node, active)
            if key in visited:
                continue
            visited.add(key)
            steps += 1
            if steps > self.policy["budgets"]["policy_steps"]:
                raise PreconditionFailed("Cycle proof exceeded inspection budget")
            if node == source.id:
                if kind == "DRAINS_TO" and inspected_cycle_evidence_id == props.get("source_evidence_id") and inspected_cycle_evidence_id:
                    self._check_evidence(props, inspection=True)
                    return
                raise PreconditionFailed("Forbidden relationship cycle")
            for edge in edges:
                if edge.source == node:
                    overlap = active if kind in self.policy["permanent_dag"] else intersection(active, interval(edge.properties))
                    if overlap is not None:
                        queue.append((edge.target, overlap))

    def create_relationship(self, kind: str, source_id: str, target_id: str, properties: dict, *, inspected_cycle_evidence_id: str | None = None) -> EdgeRecord:
        with self._session() as session:
            source, target = self.get_node(source_id), self.get_node(target_id)
            statement = self.registry.edge_statement(kind, source.kind, source.properties, target.kind, target.properties, properties)
            if self._edge_optional(properties["id"]) or self._node_optional(properties["id"]):
                raise Conflict("Application relationship ID already exists")
            self._relationship_policies(kind, source, target, properties, inspected_cycle_evidence_id=inspected_cycle_evidence_id)
            self._commit(session, "edge", properties["id"], "", statement.query.split(" RETURN r.id")[0], statement.params, "r")
        return self.get_relationship(properties["id"])

    def update_relationship(self, id: str, changes: dict, *, expected_hash: str, inspected_cycle_evidence_id: str | None = None) -> EdgeRecord:
        if not isinstance(changes, dict):
            raise SchemaError("Changes must be an object")
        with self._session() as session:
            old = self.get_relationship(id)
            if old.content_hash != expected_hash:
                raise PreconditionFailed("Stale relationship content hash")
            if set(changes).intersection({"id", "municipality_id", "created_at"}):
                raise PreconditionFailed("Relationship identity/origin cannot change")
            props = {**old.properties, **changes}
            source, target = self.get_node(old.source), self.get_node(old.target)
            self._relationship_policies(old.kind, source, target, props, exclude=id,
                                        inspected_cycle_evidence_id=inspected_cycle_evidence_id)
            body = f"MATCH (s:CivicEntity {{id:$source}})-[r:{old.kind} {{id:$id}}]->(t:CivicEntity {{id:$target}}) SET r=$props"
            self._commit(session, "edge", id, old.content_hash, body,
                         {"source": old.source, "target": old.target, "id": id, "props": props}, "r")
        return self.get_relationship(id)
