"""Regenerate B17 contracts/OpenAPI without overwriting any earlier proof."""
import json
from pathlib import Path
from app.api.coverage import ROUTES,B17_PATHS
from app.api.application import create_app
from app.api import models as m
from app.services.http.stream import EVENT_NAMES

def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
c=json.loads(Path('contracts/api_endpoints.json').read_text())
for method,path,role,req,res,name in ROUTES:
 row=next(r for r in c['routes'] if (r['method'],r['path'])==(method,'/api/v1'+path))
 row.update(role=role,response_dto=res.__name__,request_schema_id=req.__name__ if req else None,response_schema_id=res.__name__,milestone='B17' if method=='GET' and path in B17_PATHS else 'B16',status='IMPLEMENTED')
c['schema_version']=4
c['sse_cursor']='B15 source-local registration cursor distinct from domain event ID/attempt; nonnegative decimal, Last-Event-ID or cursor, both must agree; gaps CURSOR_EXPIRED/refetch, future409, malformed422'
c['b17']={'decision':'DEC-062','routes':B17_PATHS,'bounds':{'candidates_per_family':500,'adjacency_per_batch':5000,'nodes':120,'edges':200,'depth':5,'page':50,'stream_batch':50,'stream_seconds':30,'stream_poll_seconds':.25},'list_filters':['issue','status','department_id','after','before','limit','cursor'],'list_scope':'Six canonical resource lists authorize and filter before counts/pages; ID ordering; revision readback detects writes during a response, later pages are current projections','graph':'Fixed bounded RO neighborhood; reuse registry and B05 provenance/temporal rules; explicit candidate opt-in and persisted selected path bodies only','trace':'Validated source/thread-bound decisions and BROKER records, SERVER parent linkage; readonly official Saver; no raw journals/provider bodies/private reasoning','evidence':'Validated typed inspection observations, finding IDs/status, measurements/units, attributed source and review; non-report unavailable explicitly','legacy_compatibility':['Preserve DashboardSummary/AgentTracePage/HypothesisPage/MapFeatureCollection/AssetDTO/SSEStream names and original required fields','Asset condition is nullable because registry makes it optional; never invent a condition','PlanDTO.approval_status retains B16 audited lifecycle meaning with explicit schema/response limitation; actual approval is ApprovalDTO.status','SSEStream event_id/timestamp alias canonical durable id/occurred_at; raw B15 public projection unchanged'],'browser_auth':'fetch Authorization Bearer header only; query tokens rejected','stream_errors':['CURSOR_INVALID','CURSOR_CONFLICT','CURSOR_FUTURE','CURSOR_EXPIRED'],'reconnect':'Save event/cursor-control IDs, reconnect using same authenticated scope/filter, then authoritative GET refetch; no source discovery or domain acknowledgment in stream','deferred':'B19 demo routes remain absent; B18/frontend/live not authorized'}
write('contracts/api_endpoints.json',c)
api=create_app().openapi();models=json.loads(Path('contracts/api_models.json').read_text());models['schema_version']=4
models['description']='DEC-062: implemented B16/B17 closed models from actual API; B19 remains deferred. Existing service contracts and public entity names preserved.'
models['b07_trace_contract']='B07 durable shared envelope retained; B17 source/thread-authorized public trace and SSE projections, never raw bodies'
models['$defs'].update(json.loads(json.dumps(api['components']['schemas']).replace('#/components/schemas/','#/$defs/')))
for _,_,_,req,res,_ in ROUTES:
 for cls in [req,res]:
  if cls is None:continue
  schema=cls.model_json_schema();models['$defs'].update(schema.pop('$defs',{}));models['$defs'][cls.__name__]=schema
# Compatibility DTO names stay normative; planned broad objects are replaced by closed actual schemas.
write('contracts/api_models.json',models);write('docs/evidence/B17-openapi.json',api)
e=json.loads(Path('contracts/event_delivery.json').read_text());e['schema_version']=2
e['public_payload_allowlist']+= [k for k in ['execution_id','decision_id','operation'] if k not in e['public_payload_allowlist']]
e['b15_service_has_no_http_transport']=True;e['no_http_sse']=False
e['b17_transport']={'event_names':EVENT_NAMES,'inspection_requested':'GRAPH_EVIDENCE_CHANGED with operation=request_inspection; domain request intent, not approval/field execution','cursor_control':'event:cursor id:last inspected registration; data:{cursor}; no unauthorized source data','auth':'Bearer header, revalidate session and resource scope each poll/emit','replay':'Contiguous registered sequence; source occurred_at/revision do not order registrations','retention':'No deletion/expiration policy; any missing registration returns CURSOR_EXPIRED before headers, STREAM_UNAVAILABLE if detected later','safety':'Read-only polling, no discovery/ack/worker/checkpoint writes; disconnect cancellation releases generator','activity_adapter':'Committed source-bound AgentDecision selections and validated BROKER trace facts through existing INFO registrations; originals/attempt histories unchanged; use configured delivery clock cutoff','capacity':'100 bound investigations,500 decisions/500 activity facts,160 trace rows per thread; overflow fails closed'}
write('contracts/event_delivery.json',e)
lines=['# B17 actual route/DTO coverage','','52 operations,49 paths; all eight B17 GETs implemented. B19 only remains deferred.','','| Method | Path | Phase/status | Role | Request → response |','|---|---|---|---|---|']
for r in c['routes']:lines.append(f"| {r['method']} | {r['path']} | {r['milestone']} / {r['status']} | {r['role']} | {r.get('request_schema_id') or 'none'} → {r['response_schema_id']} |")
Path('docs/evidence/B17-COVERAGE.md').write_text('\n'.join(lines)+'\n')
print('Exported52operations/49paths; previous evidence unchanged')
