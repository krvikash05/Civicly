import json
from pathlib import Path
from uuid import uuid4

import pytest
from redis.exceptions import ResponseError

from app.graph.migration import MigrationError, MigrationRunner
from app.graph.schema import Registry, SchemaError
from tests.schema_examples import asset, common, edge, ASSET_TYPES

pytestmark = pytest.mark.integration


@pytest.fixture
def raw_graph(db):
    name = "civicly_b02_test_" + uuid4().hex
    g = db.select_graph(name)
    try:
        yield g
    finally:
        if name in db.list_graphs():
            g.delete()  # Only this disposable test graph, never B01/canonical.


@pytest.fixture
def migrated(db, raw_graph):
    runner = MigrationRunner(db, raw_graph.name)
    assert runner.apply()["ready"]
    return runner


def write(graph, statement):
    return graph.query(statement.query, params=statement.params, timeout=1000)


def test_schema_operational_rerun_and_no_domain_seed(migrated):
    first = migrated.status()
    assert first["ready"] and first["migration_version"] == 1
    assert first["index_groups"] == 91 and first["constraints"] == 182
    assert all(r["status"] == "OPERATIONAL" for r in migrated._catalog("indexes"))
    assert all(r["status"] == "OPERATIONAL" for r in migrated._catalog("constraints"))
    second = migrated.apply()
    assert second["ready"] and second["history"][0]["attempts"] == 2
    assert migrated.graph.ro_query("MATCH (n:CivicEntity) RETURN count(n)").result_set == [[0]]


def test_multilabel_global_ids_and_mandatory_properties(migrated):
    g = migrated.graph
    r = Registry()
    for index, label in enumerate(ASSET_TYPES):
        props = asset(label, f"ASSET-{index}")
        assert write(g, r.node_statement(label, props)).result_set == [[props["id"]]]
        labels = g.ro_query("MATCH (n:CivicEntity {id:$id}) RETURN labels(n) LIMIT 1", params={"id": props["id"]}).result_set[0][0]
        assert set(labels) == {"CivicEntity", "InfrastructureAsset", label}
    # Duplicate across different asset subtypes is caught by common-label UNIQUE.
    with pytest.raises(ResponseError):
        write(g, r.node_statement("RoadSegment", asset("RoadSegment", "ASSET-0")))
    with pytest.raises(ResponseError):
        g.query("CREATE (:RoadSegment {id:$id})", params={"id": "MISSING-REQUIRED"})
    missing_name = asset("RoadSegment", "MISSING-NAME")
    del missing_name["name"]
    with pytest.raises(ResponseError):
        g.query("CREATE (n:RoadSegment:InfrastructureAsset:CivicEntity) SET n=$props", params={"props": missing_name})
    with pytest.raises(SchemaError):
        r.node_statement("RoadSegment", {**asset("RoadSegment", "BAD"), "unknown": 1})
    assert g.ro_query("MATCH (n:CivicEntity) RETURN count(n)").result_set == [[6]]


def test_actual_point_index_and_parameterized_native_point(migrated):
    g = migrated.graph
    props = {**common("POINT"), "name": "Synthetic point", "latitude": 25.3, "longitude": 82.9,
             "geo_point": {"latitude": 25.3, "longitude": 82.9}}
    write(g, Registry().node_statement("Location", props))
    point = g.ro_query("MATCH (n:Location {id:$id}) RETURN n.geo_point LIMIT 1", params={"id": "POINT"}).result_set[0][0]
    assert point["latitude"] == pytest.approx(25.3, abs=1e-5)
    assert point["longitude"] == pytest.approx(82.9, abs=1e-5)
    assert "Index Scan" in "\n".join(g.explain("MATCH (n:Location {id:$id}) RETURN n.id LIMIT 1", params={"id": "POINT"}))


def test_relationship_metadata_direction_temporal_and_constraints(migrated):
    r, g = Registry(), migrated.graph
    a, b = asset("DrainSegment", "A"), asset("DrainSegment", "B")
    road = asset("RoadSegment", "ROAD")
    for label, props in (("DrainSegment", a), ("DrainSegment", b), ("RoadSegment", road)):
        write(g, r.node_statement(label, props))
    props = {**edge("EDGE-A"), "valid_from": "2026-10-17T00:00:00Z", "valid_to": "2026-10-18T00:00:00Z",
             "association_status": "VERIFIED", "source_evidence_id": "SYNTHETIC-SOURCE-REF"}
    statement = r.edge_statement("DRAINS_TO", "DrainSegment", a, "DrainSegment", b, props)
    assert write(g, statement).result_set == [["EDGE-A"]]
    stored = g.ro_query("MATCH ()-[r:DRAINS_TO {id:$id}]->() RETURN properties(r) LIMIT 1", params={"id": "EDGE-A"}).result_set[0][0]
    assert dict(stored) == props
    with pytest.raises(ResponseError):
        write(g, statement)  # Actual per-type unique edge ID constraint.
    with pytest.raises(ResponseError):
        g.query("MATCH (a:DrainSegment {id:$a}),(b:DrainSegment {id:$b}) CREATE (a)-[:DRAINS_TO]->(b)", params={"a":"A", "b":"B"})
    for source_type, source, target_type, target in (
        ("RoadSegment", road, "DrainSegment", b),
        ("DrainSegment", a, "RoadSegment", road),
        ("DrainSegment", a, "DrainSegment", a),
    ):
        with pytest.raises(SchemaError):
            r.edge_statement("DRAINS_TO", source_type, source, target_type, target, edge("INVALID"))
    with pytest.raises(SchemaError):
        r.edge_statement("DRAINS_TO", "DrainSegment", a, "DrainSegment", b,
                         {**edge("INVALID"), "valid_from": "2026-10-18T00:00:00Z", "valid_to": "2026-10-17T00:00:00Z"})
    assert g.ro_query("MATCH ()-[r:DRAINS_TO]->() RETURN count(r)").result_set == [[1]]
    pipe = asset("WaterPipe", "PIPE")
    write(g, r.node_statement("WaterPipe", pipe))
    write(g, r.edge_statement("UNDERLIES", "WaterPipe", pipe, "RoadSegment", road, edge("UNDER-1")))
    with pytest.raises(SchemaError, match="direction"):
        r.edge_statement("UNDERLIES", "RoadSegment", road, "WaterPipe", pipe, edge("REVERSED"))


def test_native_constraints_are_not_type_or_endpoint_authorization(migrated):
    # Prove the precise DB limitation in an isolated graph: constraints are not CHECK rules.
    props = {**common("NATIVE-ONLY"), "name": "Synthetic zone", "zone_type": "WARD", "unexpected": 1}
    with pytest.raises(SchemaError):
        Registry().node_statement("Zone", props)
    migrated.graph.query("CREATE (n:Zone:CivicEntity) SET n=$props", params={"props": props})
    assert migrated.graph.ro_query("MATCH (n:Zone) RETURN n.unexpected LIMIT 1").result_set == [[1]]
    # Application-only validation must always precede future service writes.


def test_registry_drift_and_preexisting_partial_indexes(db, raw_graph, tmp_path):
    raw_graph.query("CREATE INDEX FOR (n:Incident) ON (n.id)")
    altered = tmp_path / "registry.json"
    data = Registry().data
    data["invariants"].append("Changed specification")
    altered.write_text(json.dumps(data))
    with pytest.raises(MigrationError, match="immutable"):
        MigrationRunner(db, raw_graph.name, Registry(altered))
    assert MigrationRunner(db, raw_graph.name).apply()["ready"]


def test_unique_constraint_requires_supporting_index(db, raw_graph):
    raw_graph.query("CREATE (:Unindexed {id:$id})", params={"id":"SYNTHETIC"})
    with pytest.raises(ResponseError):
        db.execute_command("GRAPH.CONSTRAINT", "CREATE", raw_graph.name,
                           "UNIQUE", "NODE", "Unindexed", "PROPERTIES", 1, "id")


def test_partial_migration_failure_and_non_destructive_rerun(db, raw_graph, monkeypatch):
    runner = MigrationRunner(db, raw_graph.name)
    original = runner._ensure_index
    calls = 0

    def interrupted(spec):
        nonlocal calls
        original(spec)  # Real schema operation succeeds before simulated interruption.
        calls += 1
        if calls == 5:
            raise RuntimeError("Injected interruption after real index creation")

    monkeypatch.setattr(runner, "_ensure_index", interrupted)
    with pytest.raises(RuntimeError, match="Injected"):
        runner.apply()
    assert runner._history()[0]["state"] == "FAILED"
    assert not runner.status()["ready"]
    assert len(runner._catalog("indexes")) >= 4
    fresh = MigrationRunner(db, raw_graph.name)
    assert fresh.apply()["ready"]
    history = json.loads(fresh._history()[0]["state_history"])
    assert any(e["state"] == "FAILED" for e in history)
    assert history[-1]["state"] == "READY"


def test_failed_constraint_preserves_records_and_requires_explicit_recovery(db, raw_graph):
    # Preexisting conflicting rows are preserved; migration must not erase evidence.
    props = {**common("DUPLICATE"), "name": "Synthetic duplicate", "zone_type": "WARD"}
    raw_graph.query("CREATE (n:Zone:CivicEntity) SET n=$props RETURN n.id", params={"props": props})
    raw_graph.query("CREATE (n:Zone:CivicEntity) SET n=$props RETURN n.id", params={"props": props})
    runner = MigrationRunner(db, raw_graph.name)
    with pytest.raises(MigrationError, match="FAILED"):
        runner.apply()
    assert raw_graph.ro_query("MATCH (n:Zone) RETURN count(n)").result_set == [[2]]
    assert any(row["status"] == "FAILED" for row in runner._catalog("constraints"))
    with pytest.raises(MigrationError, match="FAILED"):
        runner.apply()
    # Operator repairs only the duplicate identifier in this disposable test graph.
    raw_graph.query("MATCH (n:Zone) WITH n ORDER BY id(n) LIMIT 1 SET n.id=$id", params={"id": "REPAIRED"})
    with pytest.raises(MigrationError, match="FAILED"):
        runner.apply()
    assert runner.apply(retry_failed=True)["ready"]
    assert sorted(row[0] for row in raw_graph.ro_query("MATCH (n:Zone) RETURN n.id LIMIT 10").result_set) == ["DUPLICATE", "REPAIRED"]


def test_checksum_future_version_and_lease_fail_closed(migrated, db):
    runner, g = migrated, migrated.graph
    lock = db.connection.lock(f"civicly:schema-lock:{g.name}", timeout=30, blocking=False)
    assert lock.acquire(blocking=False)
    try:
        with pytest.raises(MigrationError, match="lease"):
            runner.apply()
    finally:
        lock.release()
    g.query("MATCH (m:CivicSchemaMigration) SET m.checksum=$bad", params={"bad": "tampered"})
    with pytest.raises(MigrationError, match="checksum"):
        runner.apply()
    assert g.ro_query("MATCH (m:CivicSchemaMigration) RETURN m.checksum").result_set == [["tampered"]]
    g.query("MATCH (m:CivicSchemaMigration) SET m.checksum=$checksum,m.version=$future", params={"checksum": runner.checksum, "future": 2})
    with pytest.raises(MigrationError, match="version"):
        runner.apply()


def test_ready_marker_cannot_hide_missing_constraint(migrated, db):
    spec = next(s for s in migrated.plan["constraints"] if s["label"] == "Location" and s["type"] == "MANDATORY")
    # External catalog drift simulated only in this disposable test graph.
    db.execute_command("GRAPH.CONSTRAINT", "DROP", migrated.graph.name, "MANDATORY", "NODE", "Location",
                       "PROPERTIES", len(spec["properties"]), *spec["properties"])
    assert migrated._history()[0]["state"] == "READY"
    assert not migrated.status()["ready"]
    assert migrated.apply()["ready"]


def test_migration_never_targets_b01_probe(db):
    before = db.select_graph("civicly_b01_runtime").ro_query(
        "MATCH (n:B01Probe {id:$id}) RETURN properties(n) LIMIT 1", params={"id":"B01-PERSISTENCE"}).result_set
    with pytest.raises(MigrationError, match="target"):
        MigrationRunner(db, "civicly_b01_runtime")
    after = db.select_graph("civicly_b01_runtime").ro_query(
        "MATCH (n:B01Probe {id:$id}) RETURN properties(n) LIMIT 1", params={"id":"B01-PERSISTENCE"}).result_set
    assert before == after and before
