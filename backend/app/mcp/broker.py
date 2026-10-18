"""Deny-by-default real MCP client. Public calls accept templates, never Cypher."""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import hashlib
import json
import time
from typing import Any

from jsonschema import Draft7Validator
from mcp import Client
from pydantic import ValidationError

from app.graph.schema import Registry, SchemaError, timestamp
from .models import (ReadResult, QueryPayload, RevisionRow, NodeRow, EdgeRow, GraphSchema,
                     NodeSchema, RelationshipSchema)
from .policy import ALLOWED, Request, REVISION_QUERY
from .runtime import CITY_GRAPH, VERSION, ROOT, server_parameters


def digest(value):
    try: raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
    except (TypeError, ValueError): raw = b'non-JSON input withheld'
    return hashlib.sha256(raw).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


class BrokerError(RuntimeError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)  # never propagate server/SDK error text or arguments


def error_code(exc):
    if isinstance(exc, BaseExceptionGroup):
        codes = [error_code(e) for e in exc.exceptions]
        return 'TIMEOUT' if 'TIMEOUT' in codes else codes[0]
    if isinstance(exc, BrokerError): return exc.code
    if isinstance(exc, TimeoutError): return 'TIMEOUT'
    if isinstance(exc, (ValidationError, SchemaError, ValueError, TypeError, KeyError)): return 'INVALID_OUTPUT'
    # SDK timeout has a structured code; never inspect/log untrusted message text.
    if getattr(getattr(exc, 'error', None), 'code', None) == -32001: return 'TIMEOUT'
    return 'TRANSPORT_FAILURE'


def parse_content(result):
    if result.is_error: raise BrokerError('TOOL_ERROR')
    if len(result.content) != 1 or result.content[0].type != 'text':
        raise BrokerError('INVALID_OUTPUT')
    raw = result.content[0].text
    if len(raw.encode()) > 262144: raise BrokerError('RESULT_LIMIT')
    data = json.loads(raw)
    if not isinstance(data, dict): raise BrokerError('INVALID_OUTPUT')
    return data


class ReadBroker:
    """Only this JSON-shaped interface is intended for future agent callers.

    Construction/session ownership is trusted application code, not a capability
    sandbox against arbitrary Python code running as the same OS user.
    """
    def __init__(self, client, traces, *, timeout=4.0, max_calls=32, source_graph=CITY_GRAPH):
        if not 0.01 <= timeout <= 10 or not 3 <= max_calls <= 64:
            raise ValueError('Invalid broker budgets')
        from app.active import require_source
        self.__graph = require_source(source_graph)
        self.__client = client
        self.__traces = traces
        self.__timeout = timeout
        self.__max_calls = max_calls
        self.__calls = 0
        self.__broken = False
        self.__lock = asyncio.Lock()
        self.__schemas = {}
        self.__inventory = None
        self.__registry = Registry()
        self.__server = None
        self.__protocol = None

    def _record(self, *, operation, status, started, clock, tool=None, args=None, rows=None, revision=None):
        self.__traces.append({'trace_version': 'B06-1', 'operation': operation,
            'server': self.__server, 'protocol_version': self.__protocol,
            'tool': tool if tool in ALLOWED else ('[unapproved]' if tool else None),
            'schema_sha256': digest(self.__schemas[tool]) if tool in self.__schemas else None,
            'inventory_sha256': self.__inventory, 'arguments_sha256': digest(args) if args is not None else None,
            'arguments_summary': 'values withheld; fixed template or validated schema arguments' if args is not None else None,
            'started_at': started, 'ended_at': now(), 'latency_ms': round((time.perf_counter()-clock)*1000, 3),
            'status': status, 'denial_reason': status if status.startswith(('DENIED', 'INVALID_ARGUMENT')) else None,
            'result_summary': {('validated_rows' if operation == 'broker/validated_call' else 'received_rows'): rows} if rows is not None else None,
            'graph_revision': revision, 'selection_rationale': None,
            'invocation_origin': ('application_or_operator; no agent implemented' if self.__graph==CITY_GRAPH else 'B10 host broker; actual model summary in separate durable shared trace')})

    async def discover(self):
        started, clock = now(), time.perf_counter()
        try:
            info = self.__client.server_info
            if info is None or info.name != 'falkordb' or info.version != VERSION:
                raise BrokerError('SERVER_IDENTITY_MISMATCH')
            self.__server = {'name': info.name, 'version': info.version}
            self.__protocol = self.__client.protocol_version
            async with asyncio.timeout(self.__timeout):
                inventory = await self.__client.list_tools()
            tools = inventory.tools
            if inventory.next_cursor is not None or len(tools) != 7 or len({t.name for t in tools}) != len(tools):
                raise BrokerError('INVENTORY_MISMATCH')
            expected = ALLOWED | {'query_graph', 'delete_graph', 'list_graphs'}
            if {t.name for t in tools} != expected: raise BrokerError('INVENTORY_MISMATCH')
            self.__inventory = digest([t.model_dump(mode='json') for t in tools])
            contract = json.loads((ROOT / 'contracts/official_mcp.json').read_text())
            if any(digest(t.input_schema) != contract['observed_input_schema_sha256'].get(t.name) for t in tools):
                raise BrokerError('TOOL_SCHEMA_MISMATCH')
            self.__schemas = {t.name: t.input_schema for t in tools if t.name in ALLOWED}
            for schema in self.__schemas.values(): Draft7Validator.check_schema(schema)
            # Full upstream schemas are trusted operator evidence, not agent tools.
            self.operator_inventory = [t.model_dump(mode='json') for t in tools]
            self._record(operation='tools/list', status='SUCCESS', started=started, clock=clock)
        except Exception as exc:
            self.__broken = True
            code = error_code(exc)
            self._record(operation='tools/list', status=code, started=started, clock=clock)
            raise BrokerError(code) from None

    def tools(self):
        # Safe broker schemas deliberately differ from arbitrary-query vendor schemas.
        schema = Request.model_json_schema()
        return [{'name': name, 'broker_request_schema': schema, 'official_schema_sha256': digest(self.__schemas[name])}
                for name in sorted(self.__schemas)]

    async def __wire(self, tool, args, *, revision=None):
        started, clock = now(), time.perf_counter()
        code, count = 'SUCCESS', None
        try:
            if self.__broken: raise BrokerError('SESSION_UNAVAILABLE')
            if self.__calls >= self.__max_calls: raise BrokerError('CALL_BUDGET')
            Draft7Validator(self.__schemas[tool]).validate(args)
            self.__calls += 1
            async with asyncio.timeout(self.__timeout):
                result = await self.__client.call_tool(tool, args, read_timeout_seconds=self.__timeout)
            data = parse_content(result)
            count = len(data.get('data', [])) if isinstance(data.get('data', []), list) else None
            return data
        except Exception as exc:
            code = error_code(exc)
            if code in {'TIMEOUT', 'TRANSPORT_FAILURE', 'INVALID_OUTPUT', 'RESULT_LIMIT'}: self.__broken = True
            raise BrokerError(code) from None
        finally:
            self._record(operation='tools/call', status=code, started=started, clock=clock, tool=tool, args=args, rows=count, revision=revision)

    async def __revision(self):
        data = QueryPayload.model_validate(await self.__wire('query_graph_readonly',
            {'graphName': self.__graph, 'query': REVISION_QUERY, 'params': {'id': '0001'}}))
        if len(data.data) != 1: raise BrokerError('INVALID_REVISION')
        row = RevisionRow.model_validate(data.data[0])
        if row.pending: raise BrokerError('GRAPH_WRITE_PENDING')
        return row.revision

    def __node_type(self, labels):
        public = set(labels) - {self.__registry.base_label}
        kinds = [k for k in public if k in self.__registry.nodes and not any(k in self.__registry.nodes.get(other, {}).get('labels', []) for other in public)]
        if len(kinds) != 1 or set(labels) != set(self.__registry.labels(kinds[0])):
            raise BrokerError('INVALID_OUTPUT')
        return kinds[0]

    def __validate(self, req, data, revision):
        common = dict(graph=req.graph, tool=req.tool, template=req.template, graph_revision=revision)
        if req.tool == 'query_graph_readonly':
            payload = QueryPayload.model_validate(data)
            if req.template == 'node':
                if len(payload.data) > 1: raise BrokerError('RESULT_LIMIT')
                rows = [NodeRow.model_validate(row) for row in payload.data]
                for row in rows:
                    kind = self.__node_type(row.labels)
                    self.__registry.validate_node(kind, row.properties)
                    if row.properties['id'] != req.id or row.properties['municipality_id'] != 'demo-city': raise BrokerError('INVALID_OUTPUT')
                return ReadResult(**common, rows=rows)
            if len(payload.data) > 101: raise BrokerError('RESULT_LIMIT')
            rows = [EdgeRow.model_validate(row) for row in payload.data]
            for row in rows:
                self.__registry._properties(self.__registry.edges[row.relationship], row.properties)
                if row.properties['municipality_id'] != 'demo-city' or row.source_id != req.id or row.source_id == row.target_id:
                    raise BrokerError('INVALID_OUTPUT')
                source, target = self.__node_type(row.source_labels), self.__node_type(row.target_labels)
                shape = self.__registry.edges[row.relationship]
                if not set(self.__registry.labels(source)) & set(shape['from']) or not set(self.__registry.labels(target)) & set(shape['to']): raise BrokerError('INVALID_OUTPUT')
                if row.properties.get('association_status') == 'VERIFIED' and not row.properties.get('source_evidence_id'): raise BrokerError('INVALID_OUTPUT')
                p = row.properties
                if timestamp(p['created_at']) > timestamp(req.as_of) or ('valid_from' in p and timestamp(p['valid_from']) > timestamp(req.as_of)) or ('valid_to' in p and timestamp(req.as_of) >= timestamp(p['valid_to'])): raise BrokerError('INVALID_OUTPUT')
            if len({r.properties['id'] for r in rows}) != len(rows): raise BrokerError('INVALID_OUTPUT')
            return ReadResult(**common, rows=rows[:100], truncated=len(rows) > 100)
        if req.tool == 'get_graph_schema':
            schema = GraphSchema.model_validate(data)
            if set(schema.nodeLabels) - (set(self.__registry.nodes) | {'CivicEntity', 'CivicSchemaMigration'}) or set(schema.relationshipTypes) - set(self.__registry.edges):
                raise BrokerError('INVALID_OUTPUT')
            if any(set(c.source + c.target) - (set(self.__registry.nodes) | {'CivicEntity'}) for c in schema.connections):
                raise BrokerError('INVALID_OUTPUT')
            # Storage labels/types do not become public ontology or expose audit values.
            labels = [s for s in schema.nodeLabels if s in self.__registry.nodes]
            types = [s for s in schema.relationshipTypes if s in self.__registry.edges]
            connections = [c.model_copy(update={'source': [l for l in c.source if l in self.__registry.nodes], 'target': [l for l in c.target if l in self.__registry.nodes]}) for c in schema.connections if c.relationship in types]
            return ReadResult(**common, schema_data=schema.model_copy(update={'nodeLabels': labels, 'relationshipTypes': types, 'connections': connections}))
        schema = NodeSchema.model_validate(data) if req.tool == 'get_node_schema' else RelationshipSchema.model_validate(data)
        shape = self.__registry.shape(req.label) if req.label else self.__registry.edges[req.relationship_type]
        if (req.label and schema.label != req.label) or (req.relationship_type and schema.relationshipType != req.relationship_type) or schema.requestedSampleSize != req.sample_size or schema.sampledCount > req.sample_size:
            raise BrokerError('INVALID_OUTPUT')
        if any(p.property not in shape['properties'] or p.frequency > schema.sampledCount for p in schema.properties): raise BrokerError('INVALID_OUTPUT')
        return ReadResult(**common, schema_data=schema)

    async def call(self, arguments: dict[str, Any]):
        started, clock = now(), time.perf_counter()
        req, code, result = None, 'SUCCESS', None
        try:
            if not isinstance(arguments, dict) or arguments.get('tool') not in ALLOWED:
                raise BrokerError('DENIED_TOOL')
            if arguments.get('graph', self.__graph) != self.__graph: raise BrokerError('DENIED_GRAPH')
            try: req = Request.model_validate({**arguments, 'graph': self.__graph}, context={'authorized_graph': self.__graph})
            except (ValidationError, SchemaError): raise BrokerError('INVALID_ARGUMENTS') from None
            async with self.__lock:
                before = await self.__revision()
                data = await self.__wire(req.tool, req.arguments(), revision=before)
                result = self.__validate(req, data, before)
                after = await self.__revision()
                if before != after: raise BrokerError('GRAPH_REVISION_CHANGED')
                return result
        except Exception as exc:
            code = error_code(exc)
            if code == 'INVALID_OUTPUT': self.__broken = True
            raise BrokerError(code) from None
        finally:
            self._record(operation='broker/validated_call', status=code, started=started, clock=clock,
                tool=req.tool if req else None, args=arguments,
                rows=len(result.rows) if result and result.rows is not None else None,
                revision=result.graph_revision if result and code == 'SUCCESS' else None)


async def _ignore_vendor_log(*args, **kwargs):
    # Vendor notifications can contain raw query/errors; never copy to traces/logs.
    pass


@asynccontextmanager
async def open_broker(traces=None, *, timeout=4.0, max_calls=32, source_graph=CITY_GRAPH, credentials=None):
    """Own initialize/list/call/shutdown in one task; fresh context reconnects."""
    traces = traces if traces is not None else []
    started, clock = now(), time.perf_counter()
    opened = False
    try:
        with server_parameters(credentials=credentials) as params:
            async with Client(params, mode='legacy', read_timeout_seconds=timeout,
                              logging_callback=_ignore_vendor_log) as client:
                traces.append({'operation': 'initialize', 'status': 'SUCCESS', 'started_at': started,
                    'ended_at': now(), 'latency_ms': round((time.perf_counter()-clock)*1000,3),
                    'server': {'name': client.server_info.name, 'version': client.server_info.version},
                    'protocol_version': client.protocol_version})
                broker = ReadBroker(client, traces, timeout=timeout, max_calls=max_calls, source_graph=source_graph)
                await broker.discover()
                opened = True
                yield broker
    except Exception as exc:
        if opened and not isinstance(exc, BrokerError):
            raise  # Consumer application failures are not MCP transport failures.
        code = error_code(exc)
        if not opened:
            traces.append({'operation': 'initialize', 'status': code, 'started_at': started, 'ended_at': now()})
        raise BrokerError(code) from None
    finally:
        traces.append({'operation': 'session/closed', 'status': 'CLOSED', 'ended_at': now()})
