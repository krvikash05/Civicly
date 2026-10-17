"""Trusted configuration; separate source-read and trace-write credentials."""
import json,os,secrets,hashlib,sys,tempfile
from pathlib import Path
from contextlib import contextmanager
from mcp import StdioServerParameters
from falkordb import FalkorDB
from redis.retry import Retry
from redis.backoff import NoBackoff
from app.mcp.runtime import ROOT,CITY_GRAPH,load_credentials,provision
from app.graph.targets import new_test_graph_name
from app.graph.migration import MigrationRunner
from .storage import TraceMigration,trace_target

CONFIG=ROOT/'.runtime/civicly-mcp.json'
TRACE_USER='civicly_mcp_trace_b07'


def load_config():
    if CONFIG.is_symlink() or CONFIG.stat().st_mode&0o077:raise ValueError('Private runtime configuration required')
    cfg=json.loads(CONFIG.read_text())
    if set(cfg)!={'trace_graph','trace_password'} or len(cfg['trace_password'])<32:raise ValueError('Invalid runtime config')
    trace_target(cfg['trace_graph']);return cfg


def configure(admin):
    provision(admin)  # reuses replacement credential; no rotation rollback
    if CONFIG.exists():cfg=load_config()
    else:
        cfg={'trace_graph':new_test_graph_name(7),'trace_password':secrets.token_urlsafe(48)}
        fd=os.open(CONFIG,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:json.dump(cfg,f)
    name=cfg['trace_graph'];MigrationRunner(admin,name).apply();status=TraceMigration(admin,name).apply()
    admin.connection.execute_command('ACL','SETUSER',TRACE_USER,'reset','on',
        '#'+hashlib.sha256(cfg['trace_password'].encode()).hexdigest(),'~'+name,'~civicly:repository-lock:'+name,
        '-@all','+ping','+info','+client|setinfo','+graph.ro_query','+graph.query','+set','+get','+del','+evalsha','+eval','+script|load')
    return {'status':'PASS','trace_migration':status,'source_graph':CITY_GRAPH,'secrets_logged':False}


@contextmanager
def connections():
    read=load_credentials();cfg=load_config()
    source=FalkorDB(host='127.0.0.1',port=6379,username=read.username,password=read.password.get_secret_value(),socket_timeout=3,socket_connect_timeout=2,max_connections=4,retry=Retry(NoBackoff(),0))
    writer=FalkorDB(host='127.0.0.1',port=6379,username=TRACE_USER,password=cfg['trace_password'],socket_timeout=3,socket_connect_timeout=2,max_connections=4,retry=Retry(NoBackoff(),0))
    try:yield source,writer,cfg['trace_graph']
    finally:
        for c in (source,writer):c.connection.close();c.connection.connection_pool.disconnect()


@contextmanager
def parameters():
    with tempfile.TemporaryDirectory(prefix='civicly-domain-') as cwd:
        yield StdioServerParameters(command=str(ROOT/'backend/.venv/bin/python'),
            args=['-m','app.mcp.civicly.server'],cwd=cwd,env={'PYTHONPATH':str(ROOT/'backend'),'PYTHONUNBUFFERED':'1'})
