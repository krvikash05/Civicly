"""Bounded local operator inputs; secrets remain in owner-only files."""
import json,os
from pathlib import Path
from app.graph.models import digest

def pairs(rows):
 result={}
 for key,value in rows:
  if key in result:raise ValueError('DUPLICATE_JSON_KEY')
  result[key]=value
 return result

def read_json(path,*,private=False):
 p=Path(path)
 if p.is_symlink() or not p.is_file() or private and p.stat().st_mode&0o077 or p.stat().st_size>131072:raise ValueError('BOUNDED_REGULAR_FILE_REQUIRED')
 with p.open() as f:return json.load(f,object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(ValueError('NONFINITE_JSON')))

def write_private(path,value):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as f:json.dump(value,f,allow_nan=False)

def scope(profile,auth):return digest([profile.graph,str(Path(auth).resolve())])
def session(path,profile,auth):
 value=read_json(path,private=True)
 if set(value)!={'version','scope','token','login_key','operator_id'} or value['version']!=1 or value['scope']!=scope(profile,auth):raise ValueError('SESSION_SOURCE_BINDING')
 if not isinstance(value['token'],str):raise ValueError('SESSION_FORMAT')
 return value
