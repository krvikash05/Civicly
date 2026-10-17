#!/usr/bin/env python3
"""Focused actual-source review ZIP, exact-byte manifest and pre/post secret checks."""
from pathlib import Path
import hashlib
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review_packages/Civicly_B05_Review.zip'
FORBIDDEN={'.git','.venv','__pycache__','.pytest_cache','.uv-cache','node_modules','volumes','review_packages','Civicly_B03_Review'}


def purpose(path):
    if '/analysis/' in path:return 'B05 typed algorithm/read/counterfactual/evaluation implementation'
    if path.startswith('backend/tests/'):return 'B05 real/unit tests, explicit synthetic fixture, benchmark or pytest helper'
    if path.startswith('backend/app/graph/'):return 'Accepted B02/B03 registry, migration, read/write and integrity dependency'
    if path.startswith('backend/app/ingestion/'):return 'Accepted B04 strict validation/import/JSON artifact dependency'
    if path.startswith('backend/app/') or path.startswith('backend/cli/'):return 'Accepted connection/configuration/health/schema CLI dependency'
    if path.startswith('contracts/'):return 'Normative schema, relationship, ingestion or B05 result/budget contract'
    if path.startswith('data/'):return 'Accepted synthetic runtime dataset/manifest or sanitized source-quality inventory'
    if path.startswith('docs/evidence/'):return 'Actual B05 commands, outputs, measurements, source audit or changes'
    if path.startswith('docs/backend/'):return 'Normative requirements/architecture/task/vendor-reference documentation'
    if path.endswith('.md'):return 'Engineering guide or append-only decision/flow/status/test/blocker history'
    return 'Pinned setup, dependency or review reproduction source'


def files():
    paths=set()
    for directory in ('backend/app/graph','backend/app/services','backend/cli'):
        paths.update(str(p.relative_to(ROOT)) for p in (ROOT/directory).rglob('*.py'))
    paths.update('backend/app/ingestion/'+name+'.py' for name in ('__init__','__main__','conversion','importer'))
    paths.update(['backend/app/__init__.py','backend/app/config.py','backend/app/graph/migrations/0001.json',
        'backend/tests/__init__.py','backend/tests/conftest.py','backend/tests/integration/conftest.py',
        'backend/tests/schema_examples.py','backend/tests/b05_fixtures.py','backend/tests/b05_benchmark.py',
        'backend/tests/unit/test_graph_algorithm_models.py','backend/tests/integration/test_graph_algorithms.py',
        'contracts/schema_registry.json','contracts/graph_access.json','contracts/dataset_ingestion.json','contracts/graph_algorithms.json',
        'data/review/B05-city-extract.json','data/ingestion/city-v3.json','data/ingestion/input-manifest.json','data/ingestion/scenario-readiness.json','data/ingestion/DATA_QUALITY.md',
        'README.md','AGENTS.md','backend/README.md','backend/SCHEMA.md','backend/GRAPH_ACCESS.md','backend/INGESTION.md','backend/ALGORITHMS.md',
        'backend/pyproject.toml','backend/uv.lock','compose.yaml','Makefile','.python-version','.env.example',
        'scripts/configure_local.py','scripts/package_b05_review.py',
        'decision.md','flow.md','task_board.md','implementation_status.md','test_log.md','blockers.md'])
    paths.update('docs/backend/'+name for name in ('00_requirements.md','01_system.md','02_graph.md','03_data.md','11_microtasks.md','12_falkordb_sources.md'))
    paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'docs/evidence').glob('B05*') if p.is_file() and p.suffix in ('.json','.txt','.md','.patch') and p.name not in ('B05-package-audit.json','B05-REVIEW_MANIFEST.md'))
    return sorted(paths)


def scan(path,data,secrets):
    if not (ROOT/path).resolve().is_relative_to(ROOT):raise ValueError('Outside repository source path')
    if set(Path(path).parts)&FORBIDDEN or Path(path).name=='.env' or Path(path).suffix in ('.pyc','.key','.pem','.zip'):
        raise ValueError('Forbidden archive path:'+path)
    if any(value in data for value in secrets):raise ValueError('Actual local secret match in:'+path)
    if re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|\bsk-[A-Za-z0-9_-]{24,}',data):raise ValueError('Credential/private-key pattern in:'+path)


def main():
    secrets=[]
    env=ROOT/'.env'
    if env.is_file():
        for line in env.read_text().splitlines():
            if '=' not in line:continue
            name,value=line.split('=',1);value=value.strip(' \"\'')
            if any(word in name.upper() for word in ('PASSWORD','SECRET','KEY','TOKEN')) and len(value)>=8:secrets.append(value.encode())
    selected=files();payload={}
    for path in selected:
        data=(ROOT/path).read_bytes();scan(path,data,secrets);payload[path]=data
    manifest=['# Civicly B05 external technical review','',
        'Actual repository files, preserving relative structure. B04 accepted baseline8aaf17c; B05 changes uncommitted for human review. Source graph algorithms read-only; no B06 work.',
        '', '## Reproduce the focused B05 checks','',
        'Use Python3.12 and pinned backend/pyproject.toml + uv.lock. Configure ignored local.env with supplied setup helper; start pinned Compose without deleting volumes. The full accepted synthetic city bundle is included because its exact manifest is required by the actual-city test; it contains no evaluator answers.',
        '', 'If the retained B04 graph does not exist on a new review machine, bootstrap it safely through the included B04 importer:',
        '', '```sh',
        'PYTHONPATH=backend backend/.venv/bin/python -m app.ingestion import --graph civicly_b04_test_a84beda80da64aacbc367a9399e07a97 --bundle data/ingestion/city-v3.json --report /tmp/civicly-review-b04-import.json',
        'backend/.venv/bin/python -m pytest backend/tests/unit/test_graph_algorithm_models.py backend/tests/integration/test_graph_algorithms.py -v -s',
        '```','',
        'Existing equal city data is a no-op; changed data conflicts, never overwrite/reset it. Full B01–B05 regression and both SPEC commands require the full repository, not this focused test subset; exact commands/results are in B05-COMMANDS.md and B05-regression-tests.txt. No live MCP/LLM/GraphRAG/API/frontend is implemented/tested by this milestone.',
        '', '## Dependencies not included','',
        '- Python interpreter, virtual environment, installed wheels/SDK runtime, Docker engine/image and database/Browser volume contents. Pins and Compose definition included.',
        '- Local.env, credentials, API/private keys, caches and Git internals. Local baseline commit hash is a reference, not bundled history.',
        '- Prior B01–B04 full test sources, legacy fixtures, specification validators and unrelated blueprint contracts; use full accepted repository for complete regression/SPEC reproduction. Required B05 test helpers are included.',
        '- Original synthetic generator/legacy source and18 municipal Markdown document bodies/GeoJSON (none supplied). Canonical bundle, input hashes and sanitized readiness are included; B05 does not retrieve document bodies. Accepted full repository preserves original payloads.',
        '- Hidden evaluator truth, scenario catalog expected answers and delayed reveal payloads; deliberately not runtime/review algorithm inputs. B19 runtime isolation remains pending.',
        '', '## Included file purpose and exact SHA256','', '| File | Purpose | SHA256 |','|---|---|---|']
    for path,data in payload.items():manifest.append(f'| `{path}` | {purpose(path)} | `{hashlib.sha256(data).hexdigest()}` |')
    manifest.append('\nREVIEW_MANIFEST.md is generated metadata; every other entry is byte-identical repository source/evidence.\n')
    manifest='\n'.join(manifest).encode();scan('REVIEW_MANIFEST.md',manifest,secrets)
    OUT.parent.mkdir(exist_ok=True);temp=OUT.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path,data in payload.items():archive.writestr(path,data)
        archive.writestr('REVIEW_MANIFEST.md',manifest)
    with zipfile.ZipFile(temp) as archive:
        if archive.testzip() is not None:raise ValueError('Archive CRC failure')
        if set(archive.namelist())!=set(payload)|{'REVIEW_MANIFEST.md'}:raise ValueError('Archive inventory mismatch')
        for path in archive.namelist():
            data=archive.read(path);scan(path,data,secrets)
            if path in payload and data!=payload[path]:raise ValueError('Archive byte mismatch:'+path)
    temp.replace(OUT)
    (ROOT/'docs/evidence/B05-REVIEW_MANIFEST.md').write_bytes(manifest)
    report={'status':'PASS','archive':str(OUT),'files':len(payload)+1,'bytes':OUT.stat().st_size,
        'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'crc':'PASS','exact_repository_bytes':'PASS',
        'secret_scan':'PASS (actual local secrets + credential/private-key patterns, before/after ZIP)',
        'excluded_sensitive_paths':'PASS','secret_values_logged':False}
    (ROOT/'docs/evidence/B05-package-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
