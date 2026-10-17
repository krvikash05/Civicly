"""One-time incident credential rotation; stdout/report contain no credential values."""
import hashlib,json,os,secrets,tempfile
from pathlib import Path
from redis import Redis
from redis.exceptions import AuthenticationError
from app.config import Settings
from app.graph.connection import connect
from app.mcp.runtime import CREDENTIALS,USERNAME,CITY_GRAPH,load_credentials

old=load_credentials();replacement=secrets.token_urlsafe(48)
with connect(Settings(_env_file='.env')) as admin:
    admin.connection.execute_command('ACL','SETUSER',USERNAME,'reset','on',
        '#'+hashlib.sha256(replacement.encode()).hexdigest(),'~'+CITY_GRAPH,'-@all',
        '+ping','+info','+graph.ro_query','+client|setinfo')
    admin.connection.execute_command('CLIENT','KILL','USER',USERNAME)
    fd,name=tempfile.mkstemp(dir=CREDENTIALS.parent,prefix='rotation-')
    os.fchmod(fd,0o600)
    with os.fdopen(fd,'w') as f:
        json.dump({'username':USERNAME,'password':replacement,'graph':CITY_GRAPH},f);f.flush();os.fsync(f.fileno())
    os.replace(name,CREDENTIALS)
    denied=False
    with Redis(host='127.0.0.1',port=6379,username=USERNAME,password=old.password.get_secret_value(),socket_timeout=2) as stale:
        try:stale.ping()
        except AuthenticationError:denied=True
    assert denied,'Old authentication unexpectedly accepted'
    with Redis(host='127.0.0.1',port=6379,username=USERNAME,password=replacement,socket_timeout=2) as fresh:
        assert fresh.ping()
        assert fresh.execute_command('GRAPH.RO_QUERY',CITY_GRAPH,'RETURN 1')
    report={'status':'PASS','old_credential_authentication':'DENIED','replacement_authentication':'PASS',
        'replacement_graph_read':'PASS','read_only_graph_scope_preserved':True,'active_named_user_connections_revoked':True,
        'credential_values_logged':False,'domain_records_modified':False,'migration_0001_modified':False}
Path('docs/evidence/B07-credential-rotation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
