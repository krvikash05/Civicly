"""Own a bounded official-client connection and close its socket pool."""

from contextlib import contextmanager
from collections.abc import Iterator

from falkordb import FalkorDB
from redis.backoff import NoBackoff
from redis.retry import Retry

from app.config import Settings


@contextmanager
def connect(settings: Settings) -> Iterator[FalkorDB]:
    client = FalkorDB(
        host=settings.host,
        port=settings.port,
        username=settings.username or None,
        password=settings.password.get_secret_value() if settings.password else None,
        socket_connect_timeout=settings.connect_timeout_seconds,
        socket_timeout=settings.socket_timeout_seconds,
        max_connections=4,
        retry=Retry(NoBackoff(), 0),
    )
    try:
        yield client
    finally:
        client.connection.close()
        client.connection.connection_pool.disconnect()
