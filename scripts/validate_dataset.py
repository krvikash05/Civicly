#!/usr/bin/env python3
"""B04 offline validation only; no database, agent or evaluator payload ingestion."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.ingestion.conversion import validate_bundle,SourceError


def main():
    bundle_path=ROOT/'data/ingestion/city-v3.json'
    if not bundle_path.is_file():
        print('NOTE: B04 converted dataset not present; no canonical data validation claimed.');return 0
    try:
        bundle=json.loads(bundle_path.read_text());validate_bundle(bundle)
        raw=json.loads((ROOT/'contracts/seed_graph_expanded.json').read_text())
        old={n['properties']['id']:n['properties'] for n in raw['nodes'] if n['label']=='Observation'}
        new={n['properties']['id']:n['properties'] for n in bundle['nodes'] if n['label']=='Observation'}
        assert len(old)==len(new)==55
        assert all(new[id]['value']==p['value_number'] and new[id]['unit']==p['unit'] and new[id]['observed_at']==p['observed_at'] for id,p in old.items())
        assert all('value_number' not in n['properties'] for n in bundle['nodes'])
        print(f"PASS B04 DATA: {bundle['manifest']['nodes']} nodes / {bundle['manifest']['relationships']} relationships; all55 numeric values/units/dates preserved; strict canonical bundle/hash validation.")
        print('NOTE: Canonical artifact validation is offline; actual DB importer/benchmark evidence is recorded separately.')
        return 0
    except (ValueError,AssertionError,KeyError) as error:
        print('FAIL B04 DATA:',str(error));return 1


if __name__=='__main__':raise SystemExit(main())
