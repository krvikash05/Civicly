"""Civicly operator interface; legacy infrastructure commands remain compatible."""
import argparse,asyncio,json,sys
from . import private

# action: accepted API method/path. No caller-controlled URL or executable query.
ACTIONS={
 'responsibility':{'submit':('POST','/responsibilities'),'review':('POST','/responsibilities/{id}/review'),'get':('GET','/responsibilities/{id}')},
 'demo':{'scenarios':('GET','/demo/scenarios'),'reset':('POST','/demo/reset'),'advance':('POST','/demo/scenarios/{id}/advance')},
 'complaint':{'create':('POST','/complaints'),'get':('GET','/complaints/{id}'),'list':('GET','/complaints')},
 'investigate':{'open':('POST','/investigations'),'get':('GET','/investigations/{id}'),'resume':('POST','/investigations/{id}/resume'),'trace':('GET','/investigations/{id}/trace'),'hypotheses':('GET','/investigations/{id}/hypotheses')},
 'hypothesis':{'propose':('POST','/investigations/{id}/hypotheses'),'assess':('POST','/hypotheses/{id}/assessments'),'get':('GET','/hypotheses/{id}')},
 'evidence':{'get':('GET','/evidence/{id}')},
 'inspect':{'request':('POST','/inspections'),'transition':('POST','/inspections/{id}/transitions'),'report':('POST','/inspections/{id}/observations'),'get':('GET','/inspections/{id}')},
 'plan':{'create':('POST','/plans'),'get':('GET','/plans/{id}'),'list':('GET','/investigations/{id}/plans'),'submit':('POST','/plans/{id}/submit-approval')},
 'approve':{'decide':('POST','/approvals/{id}/decision'),'get':('GET','/approvals/{id}'),'list':('GET','/approvals')},
 'work':{'create':('POST','/work-orders'),'get':('GET','/work-orders/{id}'),'list':('GET','/work-orders'),'status':('POST','/work-orders/{id}/status'),'progress':('POST','/work-orders/{id}/progress'),'inspect':('POST','/work-orders/{id}/inspections'),'evaluate':('POST','/work-orders/{id}/outcomes')},
 'graph':{'explain':('GET','/investigations/{id}/graph'),'neighbors':('GET','/assets/{id}/neighbors'),'asset':('GET','/assets/{id}')},
 'source':{'document':('GET','/documents/{id}'),'procedures':('GET','/procedures')},
}
ACTIONS['investigate']['list']=('GET','/investigations')
EXIT={'VALIDATION_ERROR':2,'UNAUTHORIZED':3,'PERMISSION_DENIED':3,'NOT_FOUND':4,'CONFLICT':4,'DEPENDENCY_BLOCKED':5,'READ_CAPACITY':5,'RECOVERY_REQUIRED':6}
class Parser(argparse.ArgumentParser):
 def error(self,message):
  print(json.dumps({'status':'ERROR','error':{'code':'VALIDATION_ERROR','message':'Arguments do not match the operator command contract'}}))
  raise SystemExit(2)

def parser():
 p=Parser(prog='civicly',description='SIMULATED civic operator; no live provider or automatic worker',epilog='Legacy: civicly health|migrate|schema-status [--env-file FILE]; migrate alone supports --retry-failed')
 p.add_argument('--profile',required=True);p.add_argument('--auth-store',required=True);p.add_argument('--memory-profile',required=True);p.add_argument('--session',required=True);p.add_argument('--at');p.add_argument('--format',choices=['json','text'],default='json')
 sub=p.add_subparsers(dest='group',required=True,parser_class=Parser)
 auth=sub.add_parser('auth').add_subparsers(dest='action',required=True,parser_class=Parser)
 a=auth.add_parser('login');a.add_argument('--credentials',required=True);a.add_argument('--key',required=True)
 auth.add_parser('whoami');a=auth.add_parser('logout');a.add_argument('--key',required=True)
 for group,actions in ACTIONS.items():
  commands=sub.add_parser(group).add_subparsers(dest='action',required=True,parser_class=Parser)
  for name,(method,path) in actions.items():
   a=commands.add_parser(name)
   if '{id}' in path:a.add_argument('--id',required=True)
   if method=='POST':a.add_argument('--payload',required=True);a.add_argument('--key',required=True);a.add_argument('--reviewer-session')
   if group=='demo' and name=='advance':a.add_argument('--field-session')
   if method=='GET':a.add_argument('--query',help='Closed per-route query JSON file; unsupported fields rejected')
 commands=sub.add_parser('advance').add_subparsers(dest='action',required=True,parser_class=Parser)
 for name in ['discover','run']:
  a=commands.add_parser(name);a.add_argument('--key',required=True)
  if name=='run':a.add_argument('--batches',type=int,choices=range(1,5),default=1)
 a=sub.add_parser('reset');a.add_argument('--output-dir',required=True);a.add_argument('--key',required=True)
 sub.add_parser('test',help='Bounded actual dependency readiness; no shell, full pytest, lifecycle or provider')
 return p

def key(value):
 if not isinstance(value,str) or not 1<=len(value)<=200 or any(ord(c)<33 or ord(c)>126 for c in value):raise ValueError('IDEMPOTENCY_KEY')
 return value

def output(value,mode='json'):
 if mode=='text':print('Civicly — '+value['status']+' — SIMULATED / OFFLINE; data below is persisted service output')
 print(json.dumps(value,indent=2,allow_nan=False))

def result_error(code,details=None):
 return {'status':'ERROR','error':{'code':code,'message':'Operator request failed safely; inspect supplied reconciliation IDs where present','details':details or {}},'simulation_mode':'SIMULATED'}

async def execute(args):
 from pathlib import Path
 from urllib.parse import quote
 import httpx
 from app.api.__main__ import configured_app
 from app.graph.schema import timestamp
 if args.at:timestamp(args.at)
 if hasattr(args,'key'):key(args.key)
 app=configured_app(args.profile,args.auth_store,args.memory_profile,args.at)
 async with app.router.lifespan_context(app):
  s=app.state.services;s._cli_memory_path=args.memory_profile
  async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app,raise_app_exceptions=False),base_url='http://civicly.local') as client:
   if args.group=='auth' and args.action=='login':
    from app.api.models import LoginRequest
    credentials=LoginRequest.model_validate(private.read_json(args.credentials,private=True))
    if Path(args.session).exists():
     old=private.session(args.session,s.profile,args.auth_store)
     if old['login_key']!=args.key or old['operator_id']!=credentials.operator_id:raise ValueError('SESSION_FILE_EXISTS')
     actor=s.auth.resolve(old['token']);return {'status':'OK','data':s.identity(actor),'session_saved':True,'replayed':True,'simulation_mode':'SIMULATED'},0
    response=await client.post('/api/v1/auth/demo-login',json=credentials.model_dump(mode='json')|{'demo_password':credentials.demo_password.get_secret_value()})
    if response.status_code==200:
     data=response.json()['data']
     try:private.write_private(args.session,{'version':1,'scope':private.scope(s.profile,args.auth_store),'token':data['access_token'],'login_key':args.key,'operator_id':data['operator_id']})
     except OSError:
      from app.graph.repository import OutcomeUnknown
      raise OutcomeUnknown('SESSION_SAVE_UNCERTAIN') from None
     return {'status':'OK','data':{k:v for k,v in data.items() if k!='access_token'},'session_saved':True,'simulation_mode':'SIMULATED'},0
   else:
    saved=private.session(args.session,s.profile,args.auth_store);actor=s.auth.resolve(saved['token']);headers={'Authorization':'Bearer '+saved['token']}
    if args.group in {'advance','reset'}:
     from app.active import active_scope
     with active_scope(s.profile):
      if args.group=='reset':
       from .reset import reset
       value=reset(s,args.output_dir,args.key,actor)
      else:
       from .advance import advance
       value=await advance(s,args.action,getattr(args,'batches',1),args.key,actor,saved['token'])
     return {'status':'OK','data':value,'simulation_mode':'SIMULATED','execution_mode':'B15_DETERMINISTIC_DEVELOPMENT_NO_PROVIDER'},0
    if args.group=='test':
     from app.active import active_scope
     with active_scope(s.profile):value=await s.health(True)
     return {'status':'OK' if value['status']=='ok' else 'ERROR','data':value,'simulation_mode':'SIMULATED'},0 if value['status']=='ok' else 5
    if args.group=='auth':method,path=('GET','/auth/me') if args.action=='whoami' else ('POST','/auth/logout')
    else:method,path=ACTIONS[args.group][args.action]
    if '{id}' in path:
     from pydantic import TypeAdapter
     from app.api.models import ID
     id=TypeAdapter(ID).validate_python(args.id);path=path.replace('{id}',quote(id,safe=''))
    body={} if args.group=='auth' else private.read_json(args.payload) if method=='POST' else None
    query=private.read_json(args.query) if getattr(args,'query',None) else None
    if query is not None and (not isinstance(query,dict) or any(not isinstance(v,(str,int,bool)) for v in query.values())):raise ValueError('QUERY_OBJECT')
    if hasattr(args,'key'):headers['Idempotency-Key']=args.key
    if getattr(args,'reviewer_session',None):headers['X-Reviewer-Authorization']='Bearer '+private.session(args.reviewer_session,s.profile,args.auth_store)['token']
    if getattr(args,'field_session',None):headers['X-Field-Authorization']='Bearer '+private.session(args.field_session,s.profile,args.auth_store)['token']
    response=await client.request(method,'/api/v1'+path,json=body,params=query,headers=headers)
   value=response.json()
   if response.status_code>=400:
    error=value.get('error',{});code=error.get('code','DEPENDENCY_UNAVAILABLE')
    return result_error(code,error.get('details')),EXIT.get(code,5)
   if args.group=='graph' and args.action=='explain':
    from app.active import active_scope
    from app.services.operator import explain
    with active_scope(s.profile):value['data']=explain(s.repo,args.id,value['data'],s.clock())
   return {'status':'OK',**value,'simulation_mode':'SIMULATED','execution_mode':'OPERATOR_SERVICES_NO_PROVIDER'},0

def main(argv=None):
 argv=list(sys.argv[1:] if argv is None else argv)
 if argv and argv[0] in {'health','migrate','schema-status'}:
  from .legacy import main as legacy
  return legacy(argv)
 try:
  args=parser().parse_args(argv);value,code=asyncio.run(execute(args))
 except SystemExit:raise
 except Exception as exc:
  from app.graph.repository import OutcomeUnknown,Conflict,NotFound,PreconditionFailed
  from app.services.operations.auth import Denied
  if isinstance(exc,OutcomeUnknown):
   fields={k:v for k,v in getattr(exc,'reconciliation',{}).items() if k in {'request_id','entity_id','investigation_id','plan_id'} and isinstance(v,str) and len(v)<=200}
   value=result_error('RECOVERY_REQUIRED',{'commitment':'UNKNOWN',**fields});code=6
  else:
   name='UNAUTHORIZED' if isinstance(exc,Denied) else 'CONFLICT' if isinstance(exc,(Conflict,NotFound)) else 'DEPENDENCY_BLOCKED' if isinstance(exc,PreconditionFailed) else 'VALIDATION_ERROR' if isinstance(exc,(ValueError,OSError)) else 'DEPENDENCY_UNAVAILABLE'
   value=result_error(name);code=EXIT.get(name,5)
 output(value,getattr(locals().get('args'),'format','json'));return code

if __name__=='__main__':raise SystemExit(main())
