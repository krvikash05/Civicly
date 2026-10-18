"""Read-only compatibility baseline. No backend import, network, or DB access."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / 'frontend/contracts.baseline.json'
SOURCES = ('api_endpoints.json', 'api_models.json', 'event_delivery.json', 'event_types.json')


def capture(root=ROOT):
    raw = {name: (root / 'contracts' / name).read_bytes() for name in SOURCES}
    docs = {name: json.loads(value) for name, value in raw.items()}
    routes = docs['api_endpoints.json']['routes']
    definitions = docs['api_models.json']['$defs']
    identities = [(r['method'], r['path']) for r in routes]
    if len(set(identities)) != len(identities):
        raise ValueError('Duplicate route identity')
    for route in routes:
        for field in ('request_schema_id', 'response_schema_id', 'query_schema_id'):
            name = route.get(field)
            if name and name not in definitions:
                raise ValueError(f'Missing schema: {name}')
    return {
        'format_version': 1,
        'sources': {f'contracts/{name}': hashlib.sha256(value).hexdigest()
                    for name, value in raw.items()},
        'operations': len(routes),
        'paths': len({r['path'] for r in routes}),
        'schemas': len(definitions),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true',
                        help='Explicitly accept current contracts after frontend impact review')
    args = parser.parse_args()
    try:
        current = capture()
        if args.record:
            BASELINE.write_text(json.dumps(current, indent=2) + '\n')
            print('Recorded frontend contract baseline; no backend file changed.')
        else:
            previous = json.loads(BASELINE.read_text())
            if current != previous:
                print('CONTRACT CHANGED: review frontend impact before --record. No files changed.')
                for path, digest in current['sources'].items():
                    if previous.get('sources', {}).get(path) != digest:
                        print(f'  {path}')
                return 1
            print(f"PASS: {current['operations']} operations / {current['paths']} paths / "
                  f"{current['schemas']} schemas match the reviewed frontend baseline.")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f'Contract check failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
