"""Optional private exact-key memory capability; runtime never receives writes."""
import json
from pathlib import Path
from pydantic import BaseModel,ConfigDict,SecretStr,Field,model_validator
from falkordb import FalkorDB
from graphrag_sdk import ConnectionConfig
from app.graph.repository import GraphRepository
from app.mcp.civicly.storage import ScopedClient
from .service import Memory
from .sdk import docs_target
ROOT=Path(__file__).resolve().parents[3]
PROFILE=ROOT/'.runtime/b11-active.json'
class Profile(BaseModel):
 model_config=ConfigDict(extra='forbid',frozen=True,hide_input_in_errors=True)
 docs_graph:str
 canonical_graph:str
 source_graphs:list[str]=Field(min_length=1,max_length=4)
 reader_user:str
 reader_password:SecretStr
 @model_validator(mode="after")
 def validate_scope(self):
  from app.graph.targets import is_allowed_graph_target
  docs_target(self.docs_graph)
  if not is_allowed_graph_target(self.canonical_graph):raise ValueError('Canonical scope')
  if len(set(self.source_graphs))!=len(self.source_graphs):raise ValueError('Duplicate scope')
  from app.mcp.runtime import CITY_GRAPH
  from app.graph.targets import is_disposable_graph
  for graph in self.source_graphs:
   if graph!=CITY_GRAPH and not (graph.startswith("civicly_b10_test_") and is_disposable_graph(graph)):raise ValueError("Invalid source capability")
  return self
 def connect(self):
  db=FalkorDB(host='127.0.0.1',port=6379,username=self.reader_user,password=self.reader_password.get_secret_value(),socket_timeout=3)
  memory=Memory(GraphRepository(ScopedClient(db,self.canonical_graph),self.canonical_graph),ConnectionConfig(host='127.0.0.1',port=6379,username=self.reader_user,password=self.reader_password.get_secret_value(),graph_name=self.docs_graph))
  return db,memory
 def json_private(self,path):
  import os
  raw=self.model_dump(mode='json');raw['reader_password']=self.reader_password.get_secret_value()
  fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'w') as f:json.dump(raw,f)
def configured(source_graph,path=PROFILE):
 path=Path(path)
 if not path.is_file():return None
 if path.is_symlink() or path.stat().st_mode&0o077:raise ValueError('Private memory profile required')
 p=Profile.model_validate_json(path.read_text())
 if source_graph not in p.source_graphs:return None # no memory capability for this otherwise-authorized source
 # Exact source must already be authorized by existing active profile.
 from app.active import require_source
 require_source(source_graph)
 return p
