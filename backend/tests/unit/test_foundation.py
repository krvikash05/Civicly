import asyncio

import httpx
import pytest
from fastapi import FastAPI
from pydantic import BaseModel, ValidationError

from app.config import Settings
from cli.main import main


@pytest.mark.parametrize("values", [{"port": 0}, {"port": 65536}, {"query_timeout_ms": 0},
                                   {"connect_timeout_seconds": -1}, {"graph": "unsafe graph"}])
def test_invalid_connection_configuration(values):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **values)


def test_invalid_cli_configuration_is_redacted(monkeypatch, capsys):
    monkeypatch.setenv("FALKORDB_PORT", "SECRET-not-a-port")
    monkeypatch.setenv("FALKORDB_PASSWORD", "SECRET-password")
    assert main(["health", "--env-file", "/dev/null"]) == 2
    output = capsys.readouterr().out
    assert "CONFIG_INVALID" in output
    assert "SECRET" not in output


def test_fastapi_pydantic_httpx_compatibility():
    """An isolated framework spike, not an implemented Civicly HTTP endpoint."""
    class Payload(BaseModel):
        value: int

    api = FastAPI()

    @api.post("/dependency-smoke", response_model=Payload)
    def echo(payload: Payload):
        return payload

    async def exercise():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=api), base_url="http://test") as client:
            assert (await client.post("/dependency-smoke", json={"value": 7})).json() == {"value": 7}
            assert (await client.post("/dependency-smoke", json={"value": "invalid"})).status_code == 422
            assert (await client.get("/openapi.json")).status_code == 200

    asyncio.run(exercise())
