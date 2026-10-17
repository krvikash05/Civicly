from uuid import uuid4

import pytest

from app.config import Settings
from app.graph.connection import connect


@pytest.fixture
def settings():
    # Integration targets this local Compose instance. Credentials not logged.
    settings = Settings(_env_file=".env")
    assert settings.host in {"127.0.0.1", "localhost"}, "B01 tests require the local demo database"
    return settings


@pytest.fixture
def db(settings):
    with connect(settings) as client:
        assert client.connection.ping()
        yield client


@pytest.fixture
def graph(db):
    name = "civicly_b01_test_" + uuid4().hex
    graph = db.select_graph(name)
    try:
        yield graph
    finally:
        # Delete only this test's random graph if it was materialized.
        if name in db.list_graphs():
            graph.delete()
