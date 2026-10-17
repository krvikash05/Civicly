"""B06 operator proof CLI; no general query/agent/server entry point."""
import argparse
import asyncio
import json
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from .broker import open_broker, BrokerError
from .runtime import provision, CITY_GRAPH
from .policy import NODE_QUERY, EDGE_QUERY, Request


async def proof():
    traces = []
    async with open_broker(traces) as broker:
        inventory = broker.operator_inventory
        requests = [{'tool': 'get_graph_schema'}, {'tool': 'get_node_schema', 'label': 'DrainSegment'},
                    {'tool': 'get_relationship_schema', 'relationship_type': 'DRAINS_TO'},
                    {'tool': 'query_graph_readonly', 'template': 'node', 'id': 'DRAIN-D12'},
                    {'tool': 'query_graph_readonly', 'template': 'drainage_edges', 'id': 'DRAIN-D12', 'as_of': '2026-10-17T23:00:00Z'}]
        results = [(await broker.call(r)).model_dump(mode='json') for r in requests]
        denials = []
        for r in [{'tool': 'query_graph', 'readOnly': False}, {'tool': 'delete_graph'},
                  {'tool': 'list_graphs'}, {'tool': 'query_graph_readonly', 'graph': 'civicly_docs'},
                  {'tool': 'query_graph_readonly', 'query': 'CREATE (:Forbidden)'}]:
            try: await broker.call(r)
            except BrokerError as exc: denials.append({'request_fields': sorted(r), 'status': exc.code})
            else: raise AssertionError('Unexpected allowed request')
    with connect(Settings(_env_file='.env')) as c:
        graph = c.select_graph(CITY_GRAPH)
        node = graph.ro_query(NODE_QUERY, params={'id': 'DRAIN-D12', 'scope': 'demo-city'}, timeout=1000).result_set
        edges = graph.ro_query(EDGE_QUERY, params=Request.model_validate(requests[4]).arguments()['params'], timeout=1000).result_set
        assert results[3]['rows'][0]['properties'] == node[0][1]
        expected = {row[5]['id']: row[5] for row in edges}
        assert {r['properties']['id']: r['properties'] for r in results[4]['rows']} == expected
    return {'status': 'PASS', 'graph': CITY_GRAPH, 'available_inventory': inventory,
            'allowed_tools': sorted(['query_graph_readonly', 'get_graph_schema', 'get_node_schema', 'get_relationship_schema']),
            'requests': requests, 'results': results, 'broker_denials': denials, 'traces': traces,
            'independent_official_python_client_equal': True,
            'semantics': 'Current synthetic records/candidate edges only, not a causal investigation or live-agent decision'}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['configure', 'proof'])
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    try:
        if args.command == 'configure':
            with connect(Settings(_env_file='.env')) as c: result = provision(c)
        else: result = asyncio.run(proof())
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps({'status': result['status'], 'graph': CITY_GRAPH, 'output': str(args.output) if args.output else None}))
    except (BrokerError, OSError, ValueError) as exc:
        print(json.dumps({'status': 'FAILED', 'code': getattr(exc, 'code', 'RUNTIME_SETUP_FAILURE')}))
        raise SystemExit(1) from None


if __name__ == '__main__': main()
