#!/usr/bin/env python3
"""Validate Civicly's static Codex handoff package (not a runtime integration test)."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts"


def load(name):
    return json.loads((CONTRACT / name).read_text(encoding="utf-8"))


def main():
    errors = []
    try:
        schema = load("schema_registry.json")
        tools = load("mcp_tools.json")
        machines = load("state_machines.json")
        scenarios = load("demo_scenarios.json")
        seed = load("seed_graph.json")
    except (OSError, json.JSONDecodeError) as e:
        print("FAILED: could not load contract:", e)
        return 1

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("FAILED: pip install jsonschema (needed to check the JSON schemas)")
        return 1

    nodes = schema["node_types"]
    edges = schema["relationship_types"]
    enums = schema["enums"]

    def check_props(owner, properties):
        for field, desc in properties.items():
            if "type" not in desc:
                errors.append(f"{owner}.{field} missing type")
            if "enum_ref" in desc and desc["enum_ref"] not in enums:
                errors.append(f"{owner}.{field} unknown enum_ref {desc['enum_ref']}")
            if "format" in desc and desc["format"] not in ("date-time",):
                errors.append(f"{owner}.{field} undocumented format {desc['format']}")

    if schema.get("graph_name") != "civicly_knowledge":
        errors.append("graph name differs from normative spec")
    for node_name, desc in nodes.items():
        required = set(desc["required"])
        props = desc["properties"]
        if not required.issubset(props):
            errors.append(f"{node_name}: required fields missing definitions {required - set(props)}")
        if not {"id", "schema_version", "created_at"}.issubset(required):
            errors.append(f"{node_name}: missing base required fields")
        check_props(node_name, props)
        for inherited_label in desc.get("labels", []):
            if inherited_label not in nodes:
                errors.append(f"{node_name}: unknown parent label {inherited_label}")
        if desc["immutable"] and "updated_at" in required:
            errors.append(f"{node_name}: immutable entity should not require updated_at")
    for edge_name, desc in edges.items():
        if edge_name != edge_name.upper() or not re.fullmatch(r"[A-Z_]+", edge_name):
            errors.append(f"{edge_name}: relationship names must be upper snake case")
        if not desc["from"] or not desc["to"]:
            errors.append(f"{edge_name}: endpoint types empty")
        for end in desc["from"] + desc["to"]:
            if end not in nodes:
                errors.append(f"{edge_name}: unknown endpoint {end}")
        check_props(edge_name, desc["properties"])

    if len(set(enums["issue_type"])) != 3:
        errors.append("issue_type must contain all three problem categories")
    if set(enums["issue_type"]) != {"WATERLOGGING", "ROAD_DAMAGE", "WASTE_ACCUMULATION"}:
        errors.append("invalid issue categories")
    mandatory_nodes = ["Complaint", "Incident", "ProblemCluster", "HypothesisAssessment", "Evidence", "ResolutionPlan", "ActionTask", "WorkOrder", "Approval", "CaseMemory", "DomainEvent"]
    for n in mandatory_nodes:
        if n not in nodes:
            errors.append(f"mandatory node missing {n}")
    mandatory_edges = ["REPORTS", "PART_OF", "DRAINS_TO", "SUPPORTED_BY", "CONTRADICTED_BY", "HAS_TASK", "DEPENDS_ON", "AUTHORIZED_BY", "RESULTED_IN", "LEARNED_FROM", "USED_TOOL"]
    for edge in mandatory_edges:
        if edge not in edges:
            errors.append(f"mandatory relationship missing {edge}")
    for state_name, machine in machines["machines"].items():
        if state_name not in nodes:
            errors.append(f"{state_name}: machine without matching entity")
        states = set(machine["transitions"])
        if machine["initial"] not in states:
            errors.append(f"{state_name}: unknown initial state")
        for src, destinations in machine["transitions"].items():
            if len(destinations) != len(set(destinations)):
                errors.append(f"{state_name}:{src}: duplicate transitions")
            if not set(destinations).issubset(states):
                errors.append(f"{state_name}:{src}: unknown targets {set(destinations)-states}")
            if src in destinations:
                errors.append(f"{state_name}:{src}: unintended self transition")
    if set(machines["machines"]["Approval"]["transitions"]) != set(enums["approval_status"]):
        errors.append("Approval state and enum disagree")

    tool_names = [x["name"] for x in tools["tools"]]
    if len(tool_names) != len(set(tool_names)):
        errors.append("duplicate MCP tool name")
    if len(tool_names) != 18:
        errors.append(f"expected 18 domain MCP tools, found {len(tool_names)}")
    for tool in tools["tools"]:
        name = tool["name"]
        if not tool.get("requires_mcp_runtime_call", False):
            errors.append(f"{name}: not marked as real MCP call")
        for side, obj in (("input",tool["input_schema"]),("output",tool["output_schema"])):
            try:
                Draft202012Validator.check_schema(obj)
            except Exception as e:
                errors.append(f"{name} {side}: invalid JSON Schema: {e}")
            if obj.get("additionalProperties") is not False:
                errors.append(f"{name} {side}: must forbid extra fields")
            if not set(obj.get("required",[])).issubset(obj.get("properties",{})):
                errors.append(f"{name} {side}: undefined required property")
        if tool["permission"] != "READ" and "idempotency_key" not in tool["input_schema"]["required"]:
            errors.append(f"{name}: write without required idempotency key")
        if tool["permission"] == "READ" and tool["side_effect"]:
            errors.append(f"{name}: read tool has side effect")
        if not {"status", "trace_id", "source_evidence_ids", "simulation_mode"}.issubset(tool["output_schema"]["required"]):
            errors.append(f"{name}: missing output envelope")
    for required_tool in ["find_related_incidents", "trace_infrastructure_dependencies", "retrieve_case_memory", "record_hypothesis_assessment", "propose_resolution_plan", "create_work_order", "record_intervention_outcome"]:
        if required_tool not in tool_names:
            errors.append(f"tool missing {required_tool}")

    seed_nodes = {}
    for record in seed["nodes"]:
        label, props = record["label"], record["properties"]
        if label not in nodes:
            errors.append(f"seed: unknown node label {label}")
            continue
        sid = props.get("id")
        if sid in seed_nodes:
            errors.append(f"seed: duplicate ID {sid}")
        seed_nodes[sid] = label
        required = {k for k in nodes[label]["required"] if nodes[label]["properties"][k].get("introduced_in", 1) <= props.get("schema_version", 1)}
        if not required.issubset(props):
            errors.append(f"seed {sid}: missing mandatory fields {required-set(props)}")
        all_props = nodes[label]["properties"]
        if not set(props).issubset(all_props):
            errors.append(f"seed {sid}: properties not in registry {set(props)-set(all_props)}")
        for key,val in props.items():
            desc = all_props.get(key, {})
            enum_ref = desc.get("enum_ref")
            if enum_ref and val not in enums[enum_ref]:
                errors.append(f"seed {sid}.{key}: invalid enum value {val}")
            expected_type = desc.get("type")
            if expected_type == "integer" and (not isinstance(val,int) or isinstance(val,bool)):
                errors.append(f"seed {sid}.{key}: not integer")
            if expected_type == "number" and (not isinstance(val,(int,float)) or isinstance(val,bool)):
                errors.append(f"seed {sid}.{key}: not number")
    def matches_endpoint(actual,expected):
        if actual==expected: return True
        return expected in nodes.get(actual,{}).get("labels",[])
    for rel in seed["relationships"]:
        kind=rel["type"]
        if kind not in edges:
            errors.append(f"seed: unknown edge type {kind}")
            continue
        src,dst=rel["source_id"],rel["target_id"]
        if src not in seed_nodes or dst not in seed_nodes:
            errors.append(f"seed {kind}: unresolved endpoint {src}->{dst}")
            continue
        e=edges[kind]
        if not any(matches_endpoint(seed_nodes[src],x) for x in e["from"]):
            errors.append(f"seed {kind}: invalid source label {seed_nodes[src]}")
        if not any(matches_endpoint(seed_nodes[dst],x) for x in e["to"]):
            errors.append(f"seed {kind}: invalid target label {seed_nodes[dst]}")
        if not set(rel["properties"]).issubset(e["properties"]):
            errors.append(f"seed {kind}: unknown properties {set(rel['properties'])-set(e['properties'])}")
    if seed.get("ground_truth_visible_to_agent") is not False:
        errors.append("seed: ground truth visibility must be false")

    ids = [x["id"] for x in scenarios["scenarios"]]
    if len(ids) != len(set(ids)) or len(ids) != 4:
        errors.append("expected four distinct demonstration scenarios")
    for case in scenarios["scenarios"]:
        if not set(case["issue_types"]).issubset(set(enums["issue_type"])):
            errors.append(f"{case['id']}: unknown issue type")
        if not set(case["initial_expected_actions"]).issubset(tool_names):
            errors.append(f"{case['id']}: unknown tool referenced")
        for needed in ("hidden_ground_truth", "after_evidence", "negative_variant"):
            if not case.get(needed):
                errors.append(f"{case['id']}: missing {needed}")
    if not any(len(x["issue_types"]) == 3 for x in scenarios["scenarios"]):
        errors.append("missing all-three-category scenario")
    for relative in ("README.md", "docs/backend/00_requirements.md", "docs/backend/10_evaluation.md"):
        if not (ROOT / relative).is_file():
            errors.append(f"missing {relative}")
    requirements_path = ROOT / "docs/backend/00_requirements.md"
    if requirements_path.is_file():
        requirements_text = requirements_path.read_text()
        for i in range(1, 19):
            objective = f"R{i:02}"
            if f"| {objective} |" not in requirements_text:
                errors.append(f"requirement {objective} missing from maintained requirements")

    if errors:
        print(f"FAILED: {len(errors)} issue(s)")
        for e in errors:
            print("-", e)
        return 1
    print(f"PASS: {len(nodes)} node types; {len(edges)} edge types; {len(tools['tools'])} MCP tools; "
          f"{len(machines['machines'])} state machines; {len(scenarios['scenarios'])} scenario contracts; "
          f"{len(seed_nodes)} valid seed nodes/{len(seed['relationships'])} edges; 18 objectives traced")
    print("NOTE: Supplied v1/v2 fixtures checked as legacy structure; B04 canonical artifact is checked separately below.")
    print("NOTE: Static contract validation only; actual DB/MCP/AI/frontend runtime tests remain to be implemented.")
    return 0


if __name__ == "__main__":
    result=main()
    if result:sys.exit(result)
    sys.stdout.flush()
    import subprocess
    result=subprocess.call([sys.executable,str(ROOT/'scripts/validate_dataset.py')])
    if result:raise SystemExit(result)
    result=subprocess.call([sys.executable,str(ROOT/'scripts/validate_memory.py')])
    if result:raise SystemExit(result)
    result=subprocess.call([sys.executable,str(ROOT/'scripts/validate_planning.py')])
    if result:raise SystemExit(result)
    result=subprocess.call([sys.executable,str(ROOT/'scripts/validate_operations.py')])
    if result:raise SystemExit(result)
    result=subprocess.call([sys.executable,str(ROOT/'scripts/validate_events.py')])
    if result:raise SystemExit(result)
    result=subprocess.call([sys.executable,str(ROOT/'scripts/validate_api.py')])
    if result:raise SystemExit(result)
    result=subprocess.call([sys.executable,str(ROOT/'scripts/validate_cli.py')])
    if result:raise SystemExit(result)
    result=subprocess.call([sys.executable,str(ROOT/'scripts/validate_responsibility.py')])
    if result:raise SystemExit(result)
    raise SystemExit(subprocess.call([sys.executable,str(ROOT/'scripts/validate_demo.py')]))
