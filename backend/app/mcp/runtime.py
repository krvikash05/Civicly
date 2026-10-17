"""Trusted local runtime setup. Never expose this module to agent tool selection."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import tempfile

from mcp import StdioServerParameters
from pydantic import BaseModel, ConfigDict, SecretStr

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / 'backend/mcp_runtime'
CREDENTIALS = ROOT / '.runtime/mcp-credentials.json'
CITY_GRAPH = 'civicly_b04_test_a84beda80da64aacbc367a9399e07a97'
USERNAME = 'civicly_mcp_b06'
VERSION = '1.3.0'


class RuntimeCredentials(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, hide_input_in_errors=True)
    username: str
    password: SecretStr
    graph: str


def load_credentials():
    if CREDENTIALS.is_symlink() or CREDENTIALS.stat().st_mode & 0o077:
        raise ValueError('Runtime credentials must be a private regular file')
    creds = RuntimeCredentials.model_validate_json(CREDENTIALS.read_text())
    if creds.username != USERNAME or creds.graph != CITY_GRAPH or len(creds.password.get_secret_value()) < 32:
        raise ValueError('Unexpected runtime credential scope')
    return creds


def provision(client):
    """Explicit administrator action; no graph data writes, no broad account reset."""
    CREDENTIALS.parent.mkdir(mode=0o700, exist_ok=True)
    if CREDENTIALS.exists():
        creds = load_credentials()
    else:
        creds = RuntimeCredentials(username=USERNAME, password=secrets.token_urlsafe(48), graph=CITY_GRAPH)
        fd = os.open(CREDENTIALS, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f:
            json.dump({'username': creds.username, 'password': creds.password.get_secret_value(), 'graph': creds.graph}, f)
    client.connection.execute_command('ACL', 'SETUSER', USERNAME, 'reset', 'on',
        '#' + hashlib.sha256(creds.password.get_secret_value().encode()).hexdigest(),
        '~' + CITY_GRAPH, '-@all', '+ping', '+info', '+graph.ro_query', '+client|setinfo')
    return {'status': 'PROVISIONED', 'graph': CITY_GRAPH, 'commands': ['PING', 'INFO', 'GRAPH.RO_QUERY', 'CLIENT SETINFO'],
            'credential_values_logged': False, 'reprovision_after_database_recreation': True}


@contextmanager
def server_parameters():
    """Fresh dotenv-free cwd and explicit environment; SDK inherits only OS basics."""
    creds = load_credentials()
    node = shutil.which('node')
    package = RUNTIME / 'node_modules/@falkordb/mcpserver/package.json'
    if not node or json.loads(package.read_text())['version'] != VERSION:
        raise ValueError('Install the pinned official MCP runtime with npm ci')
    with tempfile.TemporaryDirectory(prefix='civicly-mcp-') as cwd:
        yield StdioServerParameters(command=node,
            args=[str(package.parent / 'dist/index.js')], cwd=cwd,
            env={'NODE_ENV': 'production', 'ENABLE_FILE_LOGGING': 'false', 'MCP_TRANSPORT': 'stdio',
                 'FALKORDB_HOST': '127.0.0.1', 'FALKORDB_PORT': '6379',
                 'FALKORDB_USERNAME': creds.username, 'FALKORDB_PASSWORD': creds.password.get_secret_value(),
                 'FALKORDB_DEFAULT_READONLY': 'true', 'FALKORDB_STRICT_READONLY': 'true'})
