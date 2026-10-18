"""Typed FastAPI routes; closed envelopes, no domain writes or Cypher here."""
import re
from uuid import uuid4
from contextlib import asynccontextmanager
from fastapi import FastAPI,Request,Depends,Query,Header
from typing import Annotated
from starlette.responses import StreamingResponse
from fastapi.exceptions import RequestValidationError,ResponseValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from pydantic import ValidationError
from redis.exceptions import RedisError
from app.active import active_scope
from app.graph.repository import NotFound,Conflict,PreconditionFailed,OutcomeUnknown,RepositoryError
from app.services.operations.auth import Denied
from app.services.planning.service import PlanningBlocked
from app.memory.models import SourceError
from app.services.demo.errors import DemoBlocked
from .dependencies import services,authenticated,HTTPFailure
from .coverage import ROUTES
from . import models as m
from .view_models import VIEW_QUERY_FIELDS,VIEW_QUERY_MODELS
MESSAGES={'READ_CAPACITY':'Bounded projection capacity reached; narrow the request or inspect configured source capacity','CURSOR_INVALID':'Cursor must be a supported nonnegative decimal registration cursor','CURSOR_CONFLICT':'Header and query cursors conflict','CURSOR_FUTURE':'Cursor exceeds the current registered stream','CURSOR_EXPIRED':'Durable cursor unavailable; refetch authoritative resources','VALIDATION_ERROR':'Request does not match the closed contract','UNAUTHORIZED':'A valid active demo session is required','PERMISSION_DENIED':'This identity is not authorized for the requested resource or action','NOT_FOUND':'The requested resource is unavailable','CONFLICT':'Request identity or expected revision conflicts with stored state','DEPENDENCY_BLOCKED':'Required evidence, approval or dependency is not satisfied','RECOVERY_REQUIRED':'Outcome requires operator reconciliation; do not automatically retry','GRAPH_UNAVAILABLE':'Graph dependency is unavailable','EXTERNAL_UNAVAILABLE':'Required configured dependency is unavailable','MCP_TOOL_ERROR':'MCP dependency failed','INTERNAL_ERROR':'Request could not be completed safely'}
def create_app(configured=None,*,lifespan=None):
 app=FastAPI(title='Civicly B16 local service API',version='1.0.0',lifespan=lifespan)
 app.state.services=configured
 @app.middleware('http')
 async def correlation(request,call_next):
  supplied=request.headers.get('X-Request-ID','')
  # Do not echo attacker-controlled text, tokens or pseudo-identities.
  request.state.request_id=supplied if re.fullmatch(r'[0-9a-f]{32}',supplied) else uuid4().hex
  try:response=await call_next(request)
  except Exception:response=error(request,500,'INTERNAL_ERROR')
  response.headers['X-Request-ID']=request.state.request_id;response.headers['Cache-Control']='no-store'
  return response
 def error(request,status,code,details=None):
  value=m.ErrorEnvelope(error=m.ErrorBody(code=code,message=MESSAGES[code],details=m.ErrorDetails(**(details or {})),retryable=False),request_id=getattr(request.state,'request_id',uuid4().hex))
  return JSONResponse(value.model_dump(mode='json'),status_code=status,headers={'WWW-Authenticate':'Bearer'} if status==401 else None)
 @app.exception_handler(Exception)
 async def exceptions(request,e):
  if isinstance(e,HTTPFailure):return error(request,e.status,e.code,e.details)
  if isinstance(e,OutcomeUnknown):
   d={'correlation_id':getattr(e,'correlation_id',request.state.request_id),'commitment':'UNKNOWN'}
   ctx=getattr(e,'reconciliation',{})
   for k in ['entity_id','investigation_id','plan_id','request_id']:
    v=ctx.get(k)
    if isinstance(v,str) and len(v)<=200:d[k]=v
   return error(request,409,'RECOVERY_REQUIRED',d)
  if isinstance(e,Denied):return error(request,403,'PERMISSION_DENIED')
  if isinstance(e,NotFound):return error(request,404,'NOT_FOUND')
  if isinstance(e,Conflict):return error(request,409,'CONFLICT')
  if isinstance(e,DemoBlocked):return error(request,409,'DEPENDENCY_BLOCKED',{'blocker_code':e.blocker_code})
  if isinstance(e,(PreconditionFailed,PlanningBlocked)):return error(request,409,'DEPENDENCY_BLOCKED')
  if isinstance(e,(RedisError,SourceError)):return error(request,503,'GRAPH_UNAVAILABLE' if isinstance(e,RedisError) else 'EXTERNAL_UNAVAILABLE')
  if isinstance(e,(RequestValidationError,ValidationError,ValueError)):return error(request,422,'VALIDATION_ERROR')
  if isinstance(e,HTTPException):return error(request,e.status_code,'NOT_FOUND' if e.status_code==404 else 'VALIDATION_ERROR')
  return error(request,500,'INTERNAL_ERROR')
 for cls in [HTTPFailure,OutcomeUnknown,Denied,NotFound,Conflict,PreconditionFailed,PlanningBlocked,RedisError,SourceError,RequestValidationError,ValidationError,ValueError,HTTPException,ResponseValidationError]:app.add_exception_handler(cls,exceptions)
 def endpoint(method,path,role,input_model,output_model,name):
  public=role=='PUBLIC';dep=Depends(services) if public else Depends(authenticated)
  def prepare(request,principal):
   s=request.app.state.services
   actor=None if public else principal.actor;token=None if public else principal.token
   if not public and role!='ANY' and actor.role not in role.split(','):raise HTTPFailure(403,'PERMISSION_DENIED')
   if set(request.query_params)-({'limit','cursor'} if method=='GET' and ('list:' in name or name in {'plans','procedures','memory','monitoring','outcomes'}) else set()) or any(len(request.query_params.getlist(k))!=1 for k in request.query_params):raise ValueError('UNKNOWN_QUERY_FIELD')
   return s,actor,token
  if method=='GET' and name in VIEW_QUERY_MODELS:
   async def view(request:Request,filters,principal=dep):
    s=request.app.state.services
    if role!='ANY' and principal.actor.role not in role.split(','):raise HTTPFailure(403,'PERMISSION_DENIED')
    supplied=set(request.query_params)
    if supplied-set(VIEW_QUERY_FIELDS[name]) or any(len(request.query_params.getlist(k))!=1 for k in supplied):raise ValueError('UNKNOWN_OR_REPEATED_QUERY_FIELD')
    filters=m.ReadFilters.model_validate(filters.model_dump())
    from app.services.http.views import Views
    from app.graph.analysis.reader import AnalysisBudgetExceeded
    try:
     with active_scope(s.profile):value=Views(s,principal.actor,principal.token,filters).run(name,request.path_params.get('id'))
    except AnalysisBudgetExceeded:raise HTTPFailure(409,'READ_CAPACITY') from None
    except PreconditionFailed as e:
     if str(e) in {'VIEW_CAPACITY','VIEW_ADJACENCY_CAPACITY','ACTIVITY_CAPACITY','TRACE_CAPACITY','SELECTED_PATH_CAPACITY','READ_EDGE_LIMIT'}:raise HTTPFailure(409,'READ_CAPACITY') from None
     raise
    return {'data':value,'request_id':request.state.request_id,'schema_version':1}
   view.__annotations__['filters']=Annotated[VIEW_QUERY_MODELS[name],Query()]
   return view
  if name=='stream':
   async def stream(request:Request,principal=dep,cursor:str|None=Query(None,max_length=32),investigation_id:str|None=Query(None,min_length=1,max_length=200),last_event_id:str|None=Header(None,alias='Last-Event-ID',max_length=32)):
    if set(request.query_params)-{'cursor','investigation_id'} or any(len(request.query_params.getlist(k))!=1 for k in request.query_params):raise ValueError('UNKNOWN_OR_REPEATED_QUERY_FIELD')
    from app.services.http.stream import Stream,cursor_value
    s=request.app.state.services;feed=Stream(s,principal.token,principal.actor,cursor_value(cursor,last_event_id),investigation_id)
    with active_scope(s.profile):feed.validate()
    return StreamingResponse(feed.events(request),media_type='text/event-stream',headers={'Cache-Control':'no-store','X-Accel-Buffering':'no'})
   return stream
  if method=='GET':
   async def get(request:Request,principal=dep,limit:int=Query(25,ge=1,le=50),cursor:str|None=Query(None,min_length=1,max_length=200)):
    s,actor,token=prepare(request,principal)
    if name in {'live','ready'}:
     value=await s.health(name=='ready')
     result=m.Success[output_model](data=value,request_id=request.state.request_id)
     if value['status']=='unavailable':return JSONResponse(result.model_dump(mode='json'),status_code=503)
     return result
    if name=='me':value=s.identity(actor)
    else:
     with active_scope(s.profile):value=await s.read(name,request.path_params.get('id'),actor,token,limit,cursor)
    return {'data':value,'request_id':request.state.request_id,'schema_version':1}
   if name.startswith('list:') or name in {'plans','procedures','memory','monitoring','outcomes'}:return get
   async def detail(request:Request,principal=dep):return await get(request,principal,25,None)
   return detail
  async def post(request:Request,body,principal=dep,idempotency_key:str|None=Header(None,alias='Idempotency-Key',min_length=1,max_length=200),reviewer_authorization:str|None=Header(None,alias='X-Reviewer-Authorization',max_length=256),field_authorization:str|None=Header(None,alias='X-Field-Authorization',max_length=256)):
   s,actor,token=prepare(request,principal)
   if name=='login':
    try:value=s.login(body)
    except Denied:raise HTTPFailure(401,'UNAUTHORIZED') from None
   elif name=='logout':s.auth.logout(token);value={'status':'LOGGED_OUT'}
   else:
    if reviewer_authorization and name not in {'inspect','demo_advance'}:raise HTTPFailure(403,'PERMISSION_DENIED')
    reviewer=None
    if reviewer_authorization:
     if not reviewer_authorization.startswith('Bearer '):raise HTTPFailure(401,'UNAUTHORIZED')
     reviewer=reviewer_authorization[7:]
     try:s.auth.resolve(reviewer)
     except Denied:raise HTTPFailure(401,'UNAUTHORIZED') from None
    field=None
    if field_authorization:
     if name!='demo_advance':raise HTTPFailure(403,'PERMISSION_DENIED')
     if not field_authorization.startswith('Bearer '):raise HTTPFailure(401,'UNAUTHORIZED')
     field=field_authorization[7:]
     try:s.auth.resolve(field)
     except Denied:raise HTTPFailure(401,'UNAUTHORIZED') from None
    with active_scope(s.profile):value=await s.command(name,path,request.path_params.get('id'),body,actor,token,idempotency_key,output_model,reviewer,**({'field_token':field} if name=='demo_advance' else {}))
   return {'data':value,'request_id':request.state.request_id,'schema_version':1}
  post.__annotations__['body']=input_model
  return post
 errors={status:{'model':m.ErrorEnvelope} for status in [401,403,404,409,422,429,502,503,500]}
 for method,path,role,input_model,output_model,name in ROUTES:
  app.add_api_route('/api/v1'+path,endpoint(method,path,role,input_model,output_model,name),methods=[method],name=method+' '+path,response_class=StreamingResponse if name=='stream' else __import__('starlette.responses',fromlist=['JSONResponse']).JSONResponse,response_model=None if name=='stream' else m.Success[output_model],responses={**errors,**({200:{'content':{'text/event-stream':{'schema':{'type':'string'}}},'description':'Persisted typed events; SSEEvent JSON with cursor control frames'}} if name=='stream' else {})})
 return app
