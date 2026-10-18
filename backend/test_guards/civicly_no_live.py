"""Ordinary-test outbound Gemini interlock, inherited by Python child processes."""
import json,os,socket,subprocess
from urllib.parse import urlparse

def provider(host):
    host=str(host).lower().rstrip('.')
    return host=='generativelanguage.googleapis.com' or host=='aiplatform.googleapis.com' or host.endswith('.aiplatform.googleapis.com')

def deny(host,layer):
    if not provider(host):return
    path=os.environ.get('CIVICLY_REQUEST_AUDIT_FILE')
    if path:
        data={'event':'BLOCKED_PROVIDER_REQUEST','host':str(host),'layer':layer,'pid':os.getpid(),'negative_probe':os.environ.get('CIVICLY_GUARD_PROBE')=='1','external_requests_sent':0}
        fd=os.open(path,os.O_WRONLY|os.O_APPEND|os.O_CREAT,0o600)
        try:os.write(fd,(json.dumps(data)+'\n').encode())
        finally:os.close(fd)
    raise RuntimeError('LIVE_GEMINI_HTTP_DISABLED_IN_ORDINARY_TESTS')

def install():
    if os.environ.get('CIVICLY_TEST_NO_LIVE')!='1' or getattr(socket,'_civicly_guard',False):return
    socket._civicly_guard=True
    original=socket.getaddrinfo
    def lookup(host,*args,**kw):deny(host,'DNS');return original(host,*args,**kw)
    socket.getaddrinfo=lookup
    try:
        import httpx
        sync=httpx.HTTPTransport.handle_request;asyn=httpx.AsyncHTTPTransport.handle_async_request
        def request(self,req):deny(req.url.host,'HTTPX');return sync(self,req)
        async def arequest(self,req):deny(req.url.host,'HTTPX_ASYNC');return await asyn(self,req)
        httpx.HTTPTransport.handle_request=request;httpx.AsyncHTTPTransport.handle_async_request=arequest
    except ImportError:pass
    popen=subprocess.Popen
    class GuardedPopen(popen):
        def __init__(self,*args,**kw):
            env=dict(os.environ if kw.get('env') is None else kw['env']);env['CIVICLY_TEST_NO_LIVE']='1'
            env['CIVICLY_REQUEST_AUDIT_FILE']=os.environ.get('CIVICLY_REQUEST_AUDIT_FILE','')
            root=os.path.dirname(__file__);old=env.get('PYTHONPATH','')
            env['PYTHONPATH']=root+(os.pathsep+old if old else '')
            kw['env']=env;super().__init__(*args,**kw)
    subprocess.Popen=GuardedPopen
