"""B16 generated schema/route parity. Static validation is not runtime evidence."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.api.coverage import ROUTES,DEFERRED_B17,DEFERRED_B19
from app.api.application import create_app
from app.api import models
from app.api.view_models import VIEW_QUERY_FIELDS,VIEW_QUERY_MODELS
from jsonschema import Draft202012Validator
c=json.loads((ROOT/'contracts/api_endpoints.json').read_text());d=json.loads((ROOT/'contracts/api_models.json').read_text())
api=create_app().openapi();actual={(method.upper(),path) for path,row in api['paths'].items() for method in row}
expected={(method,'/api/v1'+path) for method,path,*_ in ROUTES}
assert actual==expected
core=[r for r in c['routes'] if r['milestone'] in {'B16','B17','B19','B20-R-OWNERSHIP','FRONTEND-BACKEND-DEMO'}];assert {(r['method'],r['path']) for r in core}==actual
assert len(actual)==59 and len(api['paths'])==55
for method,path,role,req,res,name in ROUTES:
 row=next(r for r in core if (r['method'],r['path'])==(method,'/api/v1'+path));assert row['role']==role
 for cls in [req,res]:
  if cls is None:continue
  schema=cls.model_json_schema();schema.pop('$defs',None)
  assert schema==d['$defs'][cls.__name__],cls.__name__
  assert schema.get('additionalProperties') is False
 if method=='GET':
  actual_query={v['name'] for v in api['paths']['/api/v1'+path]['get'].get('parameters',[]) if v['in']=='query'}
  assert set(row['query_parameters'])==actual_query
  if name in VIEW_QUERY_MODELS:
   cls=VIEW_QUERY_MODELS[name];schema=cls.model_json_schema();schema.pop('$defs',None)
   assert actual_query==set(VIEW_QUERY_FIELDS[name])==set(cls.model_fields)
   assert row['query_schema_id']==cls.__name__ and schema==d['$defs'][cls.__name__]
 assert row['idempotency_key']==(method=='POST' and name not in {'login','logout'})
assert not DEFERRED_B17
from app.api.coverage import B17_PATHS
for path in B17_PATHS:assert ('GET','/api/v1'+path) in actual
assert set(api['paths']['/api/v1/events/stream']['get']['responses']['200']['content'])=={'text/event-stream'}
for path in DEFERRED_B19:assert '/api/v1'+path not in api['paths']
for schema in d['$defs'].values():Draft202012Validator.check_schema(schema)
assert c['sse_cursor'].startswith('B15 source-local registration cursor')
assert models.SubmitRequest.model_fields['assignments'].is_required()
assert 'review' not in models.ReportRequest.model_fields
assert 'review' not in models.WorkInspectionReport.model_fields
assert 'request_id' not in models.WorkInspectionReport.model_fields
print('PASS API STATIC:59 implemented operations/55paths, including filtered investigation listing; closed typed schemas/roles/idempotency/query allowlists and SSE; no runtime/live claim')
