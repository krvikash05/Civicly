import json
from pathlib import Path

import pytest

from app.graph.schema import Registry, SchemaError
from tests.schema_examples import asset, common, edge


@pytest.mark.parametrize("change", [
    {"unexpected": 1}, {"id": ""}, {"id": "  "}, {"municipality_id": "other-city"},
    {"tenant_id": "demo-city"}, {"schema_version": 2}, {"schema_version": True},
    {"id": 123}, {"created_at": "2026-02-30T00:00:00Z"},
    {"created_at": "2026-10-17T05:30:00+05:30"}, {"design_capacity": float("nan")},
    {"design_capacity": "1.0"}, {"design_capacity": True}, {"created_at": None},
    {"design_capacity": 1 << 1000},
])
def test_strict_node_rejection(change):
    with pytest.raises(SchemaError):
        Registry().node_statement("DrainSegment", {**asset("DrainSegment", "A"), **change})


def test_missing_property_and_unknown_label_rejection():
    props = asset("RoadSegment", "A")
    del props["name"]
    with pytest.raises(SchemaError, match="Missing mandatory"):
        Registry().validate_node("RoadSegment", props)
    with pytest.raises(SchemaError, match="Unknown node"):
        Registry().validate_node("NotAType", common("A"))


def test_declared_node_enum_rejected():
    props = {**common("INC"), "issue_type": "OTHER", "subtype": "UNKNOWN", "severity": "LOW",
             "started_at": "2026-10-17T00:00:00Z", "status": "REPORTED"}
    with pytest.raises(SchemaError, match="Invalid enum"):
        Registry().validate_node("Incident", props)


@pytest.mark.parametrize("props", [
    {"association_status": "CERTAIN"},
    {"association_status": "VERIFIED"},
    {"valid_from": "2026-10-18T00:00:00Z", "valid_to": "2026-10-17T00:00:00Z"},
    {"valid_to": "2026-10-18T00:00:00Z"},
    {"source_evidence_id": ""}, {"valid_from": 5}, {"extra": 1},
])
def test_edge_temporal_enum_and_provenance_validation(props):
    with pytest.raises(SchemaError):
        Registry().edge_statement("DRAINS_TO", "DrainSegment", asset("DrainSegment", "A"),
                                  "DrainSegment", asset("DrainSegment", "B"), {**edge("E"), **props})


def test_scope_metadata_consistent_across_normative_contracts():
    root = Path(__file__).resolve().parents[3]
    scope = Registry().data["municipality_scope"]
    for file in ("state_machines.json", "mcp_tools.json", "api_endpoints.json", "api_models.json", "event_types.json"):
        assert json.loads((root / "contracts" / file).read_text())["municipality_scope"] == scope
    assert scope["field"] == "municipality_id" and scope["caller_selectable"] is False


def test_legacy_fixtures_cannot_silently_enter_canonical_graph():
    root = Path(__file__).resolve().parents[3]
    seed = json.loads((root / "contracts/seed_graph_expanded.json").read_text())
    registry = Registry()
    failures = []
    for record in seed["nodes"]:
        # Explicit test-only scope/version conversion; does not discard source properties.
        props = {**record["properties"], "schema_version": 3, "municipality_id": "demo-city"}
        try:
            registry.validate_node(record["label"], props)
        except SchemaError:
            failures.append(record["properties"]["id"])
    assert len(failures) == 55
    assert failures == [f"OBS-{i:04}" for i in range(100, 155)]
    with pytest.raises(SchemaError):
        registry.validate_node(seed["nodes"][0]["label"], seed["nodes"][0]["properties"])
