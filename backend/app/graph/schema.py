"""Strict canonical registry and schema-only write compiler (not a repository)."""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re

REGISTRY_PATH = Path(__file__).resolve().parents[3] / "contracts/schema_registry.json"
UTC_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")


class SchemaError(ValueError):
    """Rejected schema input. Messages identify fields, never their values."""


def identifier(name: str) -> str:
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
        raise SchemaError("Invalid schema identifier")
    return name


def timestamp(value: str) -> datetime:
    if not isinstance(value, str) or not UTC_TIME.fullmatch(value):
        raise SchemaError("Timestamp must be ISO 8601 UTC with Z suffix")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SchemaError("Invalid timestamp") from exc


@dataclass(frozen=True)
class Statement:
    query: str
    params: dict


class Registry:
    def __init__(self, path: Path = REGISTRY_PATH):
        raw = path.read_bytes()
        self.sha256 = hashlib.sha256(raw).hexdigest()
        self.data = json.loads(raw)
        self.nodes = self.data["node_types"]
        self.edges = self.data["relationship_types"]
        self.version = self.data["schema_version"]
        self.scope = self.data["municipality_scope"]["value"]
        self.base_label = identifier(self.data["storage"]["entity_label"])
        for name, shape in [*self.nodes.items(), *self.edges.items()]:
            identifier(name)
            for field in shape["properties"]:
                identifier(field)

    def shape(self, label: str) -> dict:
        if label not in self.nodes:
            raise SchemaError("Unknown node type")
        result = {"properties": {}, "required": []}
        for parent in self.nodes[label]["labels"]:
            inherited = self.shape(parent)
            result["properties"].update(inherited["properties"])
            result["required"].extend(inherited["required"])
        result["properties"].update(self.nodes[label]["properties"])
        result["required"] = sorted(set(result["required"] + self.nodes[label]["required"]))
        return result

    def labels(self, label: str) -> tuple[str, ...]:
        self.shape(label)
        parents = {p for parent in self.nodes[label]["labels"] for p in self.labels(parent)}
        return tuple(sorted({label, self.base_label, *parents}))

    def _properties(self, shape: dict, props: dict) -> None:
        if not isinstance(props, dict) or not all(isinstance(k, str) for k in props):
            raise SchemaError("Properties must be a string-keyed object")
        if set(props) - shape["properties"].keys():
            raise SchemaError("Unknown properties")
        if set(shape["required"]) - props.keys():
            raise SchemaError("Missing mandatory properties")
        for field, value in props.items():
            desc = shape["properties"][field]
            kind = desc["type"]
            numeric = (type(value) is int and -(1 << 63) <= value < (1 << 63)) or (
                type(value) is float and math.isfinite(value)
            )
            valid = {
                "string": isinstance(value, str),
                "integer": type(value) is int and numeric,
                "number": numeric,
                "boolean": type(value) is bool,
                "point": isinstance(value, dict),
            }.get(kind, False)
            if not valid:
                raise SchemaError(f"Incorrect property type: {field}")
            if kind == "point":
                if set(value) != {"latitude", "longitude"}:
                    raise SchemaError("Point requires latitude/longitude only")
                for coordinate, low, high in (("latitude", -90, 90), ("longitude", -180, 180)):
                    v = value[coordinate]
                    if type(v) not in (int, float) or not low <= v <= high or not math.isfinite(v):
                        raise SchemaError("Invalid point coordinate")
            if "const" in desc and value != desc["const"]:
                raise SchemaError(f"Incorrect fixed property: {field}")
            if "enum" in desc and value not in desc["enum"]:
                raise SchemaError(f"Invalid enum: {field}")
            if "enum_ref" in desc and value not in self.data["enums"][desc["enum_ref"]]:
                raise SchemaError(f"Invalid enum: {field}")
            if kind in ("integer", "number"):
                if value < desc.get("minimum", -math.inf) or value > desc.get("maximum", math.inf):
                    raise SchemaError(f"Property outside bounds: {field}")
            if kind == "string":
                if len(value) < desc.get("minLength", 0) or (field in {"id", "source_evidence_id"} and not value.strip()):
                    raise SchemaError(f"Empty property: {field}")
                if desc.get("format") == "date-time":
                    timestamp(value)
        if "valid_to" in props and "valid_from" not in props:
            raise SchemaError("valid_to requires valid_from")
        if "valid_to" in props and timestamp(props["valid_to"]) <= timestamp(props["valid_from"]):
            raise SchemaError("Validity interval must be increasing")

    def validate_node(self, label: str, props: dict) -> None:
        self._properties(self.shape(label), props)
        if "updated_at" in props and timestamp(props["updated_at"]) < timestamp(props["created_at"]):
            raise SchemaError("updated_at precedes created_at")

    def validate_edge(self, kind: str, source_type: str, source: dict,
                      target_type: str, target: dict, props: dict) -> None:
        if kind not in self.edges:
            raise SchemaError("Unknown relationship type")
        self.validate_node(source_type, source)
        self.validate_node(target_type, target)
        shape = self.edges[kind]
        self._properties(shape, props)
        if not set(self.labels(source_type)).intersection(shape["from"]):
            raise SchemaError("Invalid relationship source/direction")
        if not set(self.labels(target_type)).intersection(shape["to"]):
            raise SchemaError("Invalid relationship target/direction")
        if kind in {"DRAINS_TO", "DEPENDS_ON"} and source["id"] == target["id"]:
            raise SchemaError("Self relationship forbidden")
        if props.get("association_status") == "VERIFIED" and not props.get("source_evidence_id"):
            raise SchemaError("VERIFIED association requires evidence reference")

    def node_statement(self, label: str, props: dict) -> Statement:
        self.validate_node(label, props)
        # Identifiers come only from this reviewed registry, never payload values.
        labels = ":".join(self.labels(label))
        fields = dict(props)
        point = fields.pop("geo_point", None)
        query = f"CREATE (n:{labels}) SET n=$props"
        params = {"props": fields}
        if point is not None:
            query += " SET n.geo_point=point({latitude:$lat,longitude:$lon})"
            params.update(lat=point["latitude"], lon=point["longitude"])
        return Statement(query + " RETURN n.id LIMIT 1", params)

    def edge_statement(self, kind: str, source_type: str, source: dict,
                       target_type: str, target: dict, props: dict) -> Statement:
        self.validate_edge(kind, source_type, source, target_type, target, props)
        query = (
            f"MATCH (s:{self.base_label}:{source_type} {{id:$source,municipality_id:$scope}}),"
            f"(t:{self.base_label}:{target_type} {{id:$target,municipality_id:$scope}}) "
            f"CREATE (s)-[r:{kind}]->(t) SET r=$props RETURN r.id LIMIT 1"
        )
        return Statement(query, {"source": source["id"], "target": target["id"],
                                 "scope": self.scope, "props": dict(props)})


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
