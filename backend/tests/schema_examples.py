"""Explicit synthetic examples for canonical v3 tests; not city seed data."""

NOW = "2026-10-17T00:00:00Z"
ASSET_TYPES = {"DrainSegment": "DRAIN_SEGMENT", "DrainInlet": "DRAIN_INLET",
               "RoadSegment": "ROAD_SEGMENT", "WaterPipe": "WATER_PIPE",
               "WasteCollectionPoint": "WASTE_COLLECTION_POINT", "PumpStation": "PUMP_STATION"}


def common(id):
    return {"id": id, "schema_version": 3, "municipality_id": "demo-city",
            "created_at": NOW, "updated_at": NOW}


def asset(label, id):
    return {**common(id), "name": "Synthetic asset", "asset_type": ASSET_TYPES[label],
            "operational_status": "ACTIVE"}


def edge(id):
    return {"id": id, "municipality_id": "demo-city", "created_at": NOW}
