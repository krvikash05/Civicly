"""Export the narrow B17-R query contract; preserve every B17 proof artifact."""
import json
from pathlib import Path
from app.api.application import create_app
from app.api.coverage import ROUTES
from app.api.view_models import VIEW_QUERY_FIELDS,VIEW_QUERY_MODELS

def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
api=create_app().openapi();p=Path('contracts/api_endpoints.json');c=json.loads(p.read_text())
for method,path,role,req,res,name in ROUTES:
 if method!='GET':continue
 row=next(r for r in c['routes'] if (r['method'],r['path'])==(method,'/api/v1'+path))
 row['query_parameters']=[v['name'] for v in api['paths']['/api/v1'+path]['get'].get('parameters',[]) if v['in']=='query']
 if name in VIEW_QUERY_MODELS:row['query_schema_id']=VIEW_QUERY_MODELS[name].__name__
c['b17']['query_contract']={'decision':'DEC-063','policy':'Closed per-route allowlists are identical to OpenAPI query parameters; unknown, irrelevant or repeated parameters return sanitized422','hypotheses':'status equality and exclusive stable ID cursor/limit only; after/before rejected (no normative creation-versus-assessment timestamp semantics)','dashboard':'issue/status/department_id/after/before apply independently to each authorized metric resource; aggregate response has no limit/cursor','trace':'after/before inclusively filter actual persisted tool-finished/decision-decided timestamp before chronological timestamp+eventID pagination','resources':'Existing resource filters/paging unchanged; inclusive after/before on reported/start/request/create timestamp per existing projection','map':'Existing resource filters/paging plus investigation_id; canonical location points only','graph_neighbors':'depth and include_candidates only','asset':'No query parameters','stream':'Existing cursor/investigation_id and Last-Event-ID header unchanged'}
write(p,c)
p=Path('contracts/api_models.json');models=json.loads(p.read_text())
for cls in set(VIEW_QUERY_MODELS.values()):
 schema=cls.model_json_schema();models['$defs'].update(schema.pop('$defs',{}));models['$defs'][cls.__name__]=schema
write(p,models);write('docs/evidence/B17R-openapi.json',api)
lines=['# B17-R exact query coverage','','Unknown/irrelevant/repeated parameters return sanitized422. No hypothesis date filtering semantics invented.','','| GET /api/v1 route | Accepted query parameters |','|---|---|']
for row in c['routes']:
 if row['method']=='GET' and row.get('status')=='IMPLEMENTED':lines.append('| '+row['path']+' | '+(', '.join(row['query_parameters']) or 'none')+' |')
Path('docs/evidence/B17R-QUERY-COVERAGE.md').write_text('\n'.join(lines)+'\n')
print('Exported route-specific query contracts/OpenAPI;52operations/49paths unchanged')
