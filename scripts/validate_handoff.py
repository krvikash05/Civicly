#!/usr/bin/env python3
"""Static *specification* cross-file validation. Not a runtime integration test."""
from pathlib import Path
from datetime import datetime
import json,hashlib,collections,sys,re
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text())
errors=[];warn=[]
def require(cond,msg):
 if not cond:errors.append(msg)
reg=load('contracts/schema_registry.json')
states=load('contracts/state_machines.json')
mcp=load('contracts/mcp_tools.json')
apis=load('contracts/api_endpoints.json')
api_models=load('contracts/api_models.json')
events=load('contracts/event_types.json')
cat=load('contracts/scenarios/catalog.json')
base=load('contracts/seed_graph.json')
seed=load('contracts/seed_graph_expanded.json')
bind=load('contracts/scenarios/bindings.json')['bindings']
truth=load('data/scenarios/hidden_truth.json')['cases']
reveals=load('data/scenarios/event_reveals.json')['cases']
manifest=load('data/documents/manifest.json')['documents']
N=reg['node_types'];R=reg['relationship_types']
require(reg['graph_name']=='civicly_knowledge','wrong canonical graph name')
require(len(N)>=40 and len(R)>=45,'graph registry is unexpectedly narrow')
require(states['machines']['WorkOrder']['initial']=='AUTHORIZED','WorkOrder must start AUTHORIZED after plan approval')
require('DRAFT' not in states['machines']['WorkOrder']['transitions'],'WorkOrder legacy DRAFT lifecycle not resolved')
require('create_work_order' in {t['name'] for t in mcp['tools']},'missing work-order MCP tool')
require(len(mcp['tools'])==len({t['name'] for t in mcp['tools']}),'duplicate MCP tool names')
require(len(apis['routes'])==len({(r['method'],r['path']) for r in apis['routes']}),'duplicate API endpoints')
require(any('/events/stream' in r['path'] for r in apis['routes']),'SSE endpoint missing')
for r in apis['routes']:
 require(r['response_schema_id'] in api_models['$defs'],f'unknown response schema {r["response_schema_id"]}')
 if r['method']=='POST': require(r['request_schema_id'] in api_models['$defs'],f'unknown request schema {r["request_schema_id"]}')
try:
 from jsonschema import Draft202012Validator
 for name,shape in api_models['$defs'].items():Draft202012Validator.check_schema(shape)
except ImportError:
 warn.append('jsonschema package unavailable; skipped JSON Schema meta-validation')
except Exception as exc:errors.append(f'bad API JSON Schema: {exc}')
require(any('/investigations/{id}/graph' in r['path'] for r in apis['routes']),'frontend graph DTO endpoint missing')
require('RECURRENCE_DETECTED' in events['types'] and 'AGENT_TOOL_EXECUTED' in events['types'],'critical event names missing')
require(events['delivery']['consumer_idempotent'] and events['delivery']['at_least_once'],'unsafe event delivery policy')
# Graph required properties / reference types
ids={};types={}
for n in seed['nodes']:
 label=n['label'];p=n['properties'];id=p.get('id')
 require(label in N,f'unknown node {label} {id}')
 if label not in N:continue
 require(id not in ids,f'duplicate ID {id}')
 ids[id]=n;types[id]={label,*N[label].get('labels',[])}
 for k in N[label]['required']:require(k in p,f'{id} missing {k}')
 for field in ('created_at','updated_at'):
  try:datetime.fromisoformat(p[field].replace('Z','+00:00'))
  except Exception:errors.append(f'{id} invalid {field}')

edge_set=set()
for e in seed['relationships']:
 t,s,d=e['type'],e['source_id'],e['target_id'];k=(t,s,d)
 require(k not in edge_set,f'duplicate edge {k}');edge_set.add(k)
 require(t in R,f'unknown rel type {t}')
 require(s in ids and d in ids,f'dangling edge {t}: {s}->{d}')
 if t not in R or s not in ids or d not in ids:continue
 allowed=R[t]
 require(bool(types[s].intersection(allowed['from'])),f'edge {t} source {s} wrong type')
 require(bool(types[d].intersection(allowed['to'])),f'edge {t} target {d} wrong type')
 if t in ('DRAINS_TO','DEPENDS_ON'):require(s!=d,f'self cycle {t} {s}')

require(len(seed['nodes'])>=750 and len(seed['relationships'])>=1000,'expanded seed counts too low')
from_c=collections.Counter(n['label'] for n in seed['nodes'])
for label,minimum in [('Zone',5),('Location',50),('Incident',90),('Complaint',250),('ProblemCluster',20),('PickupExecution',100)]:
 require(from_c[label]>=minimum,f'{label} count < {minimum}')
require(not seed['ground_truth_visible_to_agent'],'expanded graph cannot reveal hidden evaluation truth')
for n in base['nodes']:require(n['properties']['id'] in ids,'base seed missing node '+n['properties']['id'])
# hidden truth separation / scenario binding, covers all issues and unique IDs
scs=cat['scenarios']; names={s['id'] for s in scs}
require(len(scs)>=12 and len(names)==len(scs),'not all 12 unique cases')
require(names==set(bind)==set(truth)==set(reveals),'scenario truth/binding/reveal ID mismatch')
for sc in scs:
 sid=sc['id'];require(sc.get('ground_truth_separated') is True,f'{sid} missing evaluator isolation')
 require(sc['preferred_tool_categories'] and sc['expected_safe_next_actions'],f'{sid} no tool/action expectations')
 require(set(sc['issue_types']).issubset(reg['enums']['issue_type']),f'{sid} unknown issue type')
 for iid in bind[sid]['incident_ids']:
  require(iid in ids and 'Incident' in types.get(iid,set()),f'{sid} invalid incident {iid}')
  if iid in ids: require(ids[iid]['properties'].get('issue_type') in sc['issue_types'],f'{sid} incident issue category mismatch {iid}')
 for aid in bind[sid]['asset_ids']:require(aid in ids,f'{sid} invalid asset {aid}')
 for cid in bind[sid]['cluster_ids']:require(cid in ids and 'ProblemCluster' in types.get(cid,set()),f'{sid} invalid cluster {cid}')
 require('underlying_cause' in truth[sid],'evaluator cause missing '+sid)
 require('revealed_observation' in reveals[sid],f'missing staged inspection {sid}')
# documents provenance and hashes
require(len(manifest)>=15,'insufficient source documents')
for x in manifest:
 file=ROOT/x['file_path'];require(file.is_file(),f"document missing {x['file_path']}")
 if file.is_file():require(hashlib.sha256(file.read_bytes()).hexdigest()==x['sha256'],f"document sha mismatch {x['document_id']}")
 require(x['synthetic'] and x['source_kind']=='SYNTHETIC','unlabeled demo document')
# all audit files and microtask IDs
for p in ['AGENTS.md','CODEX_START_HERE.md','decision.md','flow.md','implementation_status.md','test_log.md','blockers.md','task_board.md','docs/backend/11_microtasks.md','docs/frontend_contract/FRONTEND_READINESS.md']:
 require((ROOT/p).exists(),f'missing handoff file {p}')
mt=(ROOT/'docs/backend/11_microtasks.md').read_text()
for i in range(26):require(f'B{i:02d}' in mt,f'B{i:02d} missing from microtask plan')
if errors:
 print('STATIC HANDOFF VALIDATION FAILED:')
 for s in errors[:80]:print(' -',s)
 print(f'{len(errors)} errors; {len(warn)} warnings');sys.exit(1)
print(f'PASS: {len(N)} entity types, {len(R)} relationships, {len(mcp["tools"])} custom MCP tools, {len(apis["routes"])} planned API routes, {len(api_models["$defs"])} typed request/response schemas, {len(events["types"])} event types')
print(f'PASS: {len(seed["nodes"])} seeded nodes, {len(seed["relationships"])} seeded relationships, {len(scs)} scenario bindings+hidden truths, {len(manifest)} sourced synthetic documents')
print('PASS: codex log files + B00-B25 microtasks + work-order approval invariant')
print('NOTE: This is STATIC blueprint verification, not a running FalkorDB/MCP/GraphRAG/AI acceptance test.')
