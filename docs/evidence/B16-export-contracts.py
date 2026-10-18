from app.api.coverage import ROUTES
from app.api.application import create_app
import json
from pathlib import Path
p=Path('contracts/api_endpoints.json');contract=json.loads(p.read_text());before=contract['routes']
for method,path,role,req,res,name in ROUTES:
 row=next((r for r in before if r['path']=='/api/v1'+path and r['method']==method),None)
 if not row:
  row={'method':method,'path':'/api/v1'+path};before.append(row)
 row.update(role=role,response_dto=res.__name__,idempotency_key=method=='POST' and name not in {'login','logout'},request_schema_id=req.__name__ if req else None,response_schema_id=res.__name__,milestone='B16',status='IMPLEMENTED')
for row in before:
 if row.get('milestone')!='B16':row.update(milestone='B19' if '/demo/' in row['path'] else 'B17',status='DEFERRED_NOT_IMPLEMENTED')
contract['schema_version']=3
contract['sse_cursor']='B15 source-local registration cursor distinct from domain event ID/attempt; B17 defines HTTP Last-Event-ID transport'
contract['dto_contracts']['PlanDTO']['required']=['plan_id','investigation_id','version','content_hash','draft','draft_receipt','status','expected_hash','approval_status','execution_gates_verified','simulated','limitations']
contract['b16_security']={'reviewer_transport':'X-Reviewer-Authorization: Bearer; authenticated independent analyst, never JSON','source_configuration':'Host-only exact private profiles; no caller graph/runtime/role selection','request_identity':'Server-generated X-Request-ID correlation; Idempotency-Key bound to server actor+path+entity+validated body+reviewer identity','recovery':'409 RECOVERY_REQUIRED UNKNOWN, persisted transport intent; no automatic redispatch','public':['POST /api/v1/auth/demo-login','GET /api/v1/health/live','GET /api/v1/health/ready'],'finite_reads':'Bound500 candidates, authorize before total/count/page; limit1..50; stable ID cursor; rich B17 views deferred'}
p.write_text(json.dumps(contract,indent=2)+'\n')
models=json.loads(Path('contracts/api_models.json').read_text());models['schema_version']=3
api=create_app().openapi();schemas=json.loads(json.dumps(api['components']['schemas']).replace('#/components/schemas/','#/$defs/'));models['$defs'].update(schemas)
for _,_,_,req,res,_ in ROUTES:
 for cls in [req,res]:
  if cls is None:continue
  value=cls.model_json_schema();nested=value.pop('$defs',{});models['$defs'].update(nested);models['$defs'][cls.__name__]=value
models['description']='Normative B16 models generated from accepted typed service adapters/OpenAPI. B17/B19 schemas remain planned; public domain names preserved. Exact draft/approval/gate semantics supersede stale transport fields per DEC-060.'
Path('contracts/api_models.json').write_text(json.dumps(models,indent=2)+'\n')
lines=['# B16 route coverage (DEC-060)','','Actual44B16operations/42paths. No501stubs. All paths have /api/v1 prefix. B17/B19 are absent from actual OpenAPI.','','| Method | Path | Phase | Role | Typed request to response |','|---|---|---|---|---|']
for row in before:lines.append('| '+row['method']+' | '+row['path']+' | '+row['milestone']+' | '+row['role']+' | '+str(row.get('request_schema_id') or 'none')+' to '+row['response_schema_id']+' |')
lines+=['','Core basic bounded pagination/authorization is B16; comprehensive map/graph/trace/dashboard/SSE and richer filtering remain B17. Scenario reset/advance/list remains B19. New B16 routes fill missing draft access, authorized order creation, independent inspection lifecycle and typed execution gates; none grants automatic work/model authority.','', 'Corrections: work-orders outcomes is analyst independent Evaluate, not caller-supplied outcome; status is B13 assignment/cancel only, B14 progress separate. Draft receipt/current lifecycle separated. Reviewer bearer token is header-only.']
Path('docs/evidence/B16-COVERAGE.md').write_text('\n'.join(lines)+'\n');Path('docs/evidence/B16-openapi.json').write_text(json.dumps(api,indent=2)+'\n')
print(len(before),'normative operations;',sum(r['milestone']=='B16' for r in before),'B16')
