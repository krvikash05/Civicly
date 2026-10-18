"""Presenter API: reject concurrent source mutations during a live wake."""
from uuid import uuid4
from starlette.responses import JSONResponse
from app.api.__main__ import configured_app
from .source import source_writer
from .runtime import HostBlocked

def api(config):
 app=configured_app(config.profile,config.auth_store,config.memory_profile)
 @app.middleware('http')
 async def serialize_writers(request,call_next):
  if request.method not in {'POST','PUT','PATCH','DELETE'} or request.url.path.startswith('/api/v1/auth/'):
   return await call_next(request)
  services=app.state.services
  if services is None:return await call_next(request)
  try:
   with source_writer(services.repo,60):return await call_next(request)
  except HostBlocked:
   return JSONResponse({'error':{'code':'DEPENDENCY_BLOCKED','message':'The demo source is running an investigation. Retry manually after it pauses.','details':{'blocker_code':'DEMO_SOURCE_BUSY'},'retryable':False},'request_id':uuid4().hex},status_code=409,headers={'Cache-Control':'no-store'})
 return app
