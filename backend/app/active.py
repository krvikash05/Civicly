"""Trusted local B10 profile. A name matching a pattern is not an authorization."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib,json,os,secrets
from pathlib import Path
from uuid import uuid4
from pydantic import BaseModel,ConfigDict,SecretStr,model_validator
from app.graph.targets import is_disposable_graph,new_test_graph_name
ROOT=Path(__file__).resolve().parents[2]

CURRENT=ContextVar('civicly_active_graph',default=None)
DEFAULT_PROFILE=ROOT/'.runtime/b10-active.json'

class ActiveProfile(BaseModel):
    model_config=ConfigDict(extra='forbid',frozen=True,hide_input_in_errors=True)
    version: int=1
    graph: str
    checkpoints: str
    read_user: str
    read_password: SecretStr
    checkpoint_user: str
    checkpoint_password: SecretStr
    @model_validator(mode='after')
    def scope(self):
        from uuid import UUID
        if self.version!=1 or not self.graph.startswith('civicly_b10_test_') or not is_disposable_graph(self.graph):raise ValueError('B10 integration graph required')
        if not self.checkpoints.startswith('civicly_b10_checkpoints_'):raise ValueError('Separate checkpoint namespace required')
        token=UUID(hex=self.checkpoints.removeprefix('civicly_b10_checkpoints_'))
        if token.version!=4 or token.hex!=self.checkpoints.removeprefix('civicly_b10_checkpoints_'):raise ValueError('Checkpoint UUID required')
        suffix=self.graph[-32:]
        if self.read_user!='civicly_b10_read_'+suffix or self.checkpoint_user!='civicly_b10_checkpoint_'+suffix:raise ValueError('Bound account names required')
        if min(len(self.read_password.get_secret_value()),len(self.checkpoint_password.get_secret_value()))<32:raise ValueError('Strong credentials required')
        return self

def new_profile():
    graph=new_test_graph_name(10);suffix=graph[-32:]
    return ActiveProfile(graph=graph,checkpoints='civicly_b10_checkpoints_'+uuid4().hex,
        read_user='civicly_b10_read_'+suffix,read_password=secrets.token_urlsafe(48),
        checkpoint_user='civicly_b10_checkpoint_'+suffix,checkpoint_password=secrets.token_urlsafe(48))

def save(profile,path=DEFAULT_PROFILE):
    path=Path(path);path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    value=profile.model_dump(mode='json');value['read_password']=profile.read_password.get_secret_value();value['checkpoint_password']=profile.checkpoint_password.get_secret_value()
    with os.fdopen(fd,'w') as f:json.dump(value,f)

def load(path=DEFAULT_PROFILE):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_mode&0o077:raise ValueError('Private regular profile required')
    return ActiveProfile.model_validate_json(path.read_text())

@contextmanager
def active_scope(profile):
    profile=ActiveProfile.model_validate(profile);token=CURRENT.set(profile)
    try:yield profile
    finally:CURRENT.reset(token)

def is_shared_target(name):
    p=CURRENT.get();return p is not None and name==p.graph

def require_source(name):
    from app.mcp.runtime import CITY_GRAPH
    if name!=CITY_GRAPH and not is_shared_target(name):raise ValueError('Source is not the trusted active graph')
    return name

def provision(admin,profile):
    # Exact-key ACLs; credentials never returned. No source record mutation.
    for user,password,graph,commands in [
        (profile.read_user,profile.read_password,profile.graph,['+graph.ro_query']),
        (profile.checkpoint_user,profile.checkpoint_password,profile.checkpoints,['+graph.ro_query','+graph.query'])]:
        admin.connection.execute_command('ACL','SETUSER',user,'reset','on','#'+hashlib.sha256(password.get_secret_value().encode()).hexdigest(),
            '~'+graph,'-@all','+ping','+info','+client|setinfo',*commands)
    return {'source_graph':profile.graph,'checkpoint_graph':profile.checkpoints,'scope':'exact keys','credentials_logged':False}
