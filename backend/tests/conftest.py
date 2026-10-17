from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def pytest_addoption(parser):
    parser.addoption(
        "--run-persistence", action="store_true", default=False,
        help="Restart and recreate only this project's civicly FalkorDB container",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-persistence"):
        for item in items:
            if "persistence" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="Use --run-persistence to authorize lifecycle checks"))
