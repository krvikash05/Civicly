"""Closed source, ownership, validity and citation contracts; no model authority."""
import hashlib,json,re
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,model_validator
from app.graph.schema import timestamp
ROOT=Path(__file__).resolve().parents[3]
OWNERS={'Drainage Operations':'DEPT-DRAIN','Road Maintenance':'DEPT-ROAD','Water Utilities':'DEPT-WATER','Sanitation Services':'DEPT-SAN','Civic Operations Coordination':'DEPT-COORD'}
class SourceError(ValueError):pass
class Source(BaseModel):
 model_config=ConfigDict(extra='forbid',strict=True,frozen=True,hide_input_in_errors=True)
 document_id:str=Field(pattern=r'^D[0-9]{3}(?:-PDF)?$')
 title:str=Field(min_length=1,max_length=200)
 municipality_id:Literal['demo-city']='demo-city'
 version:int=Field(ge=1,le=10000)
 owner_department_id:str
 source_kind:Literal['SYNTHETIC']='SYNTHETIC'
 synthetic:Literal[True]=True
 source_authority:Literal['SYNTHETIC_DEMONSTRATION']='SYNTHETIC_DEMONSTRATION'
 review_status:Literal['REVIEWED','PROPOSED','DISPUTED']
 reviewed_by:str|None=None
 effective_from:str
 effective_to:str|None=None
 file_path:str
 sha256:str=Field(pattern=r'^[0-9a-f]{64}$')
 status:Literal['ACTIVE','REVOKED']='ACTIVE'
 supersedes:int|None=Field(default=None,ge=1)
 derived_from:str|None=None
 action_types:tuple[str,...]=Field(min_length=1,max_length=12)
 @model_validator(mode='after')
 def rules(self):
  if self.owner_department_id not in OWNERS.values():raise ValueError('Unknown canonical owner')
  start=timestamp(self.effective_from)
  if self.effective_to and timestamp(self.effective_to)<=start:raise ValueError('Invalid validity interval')
  if self.review_status=='REVIEWED' and not self.reviewed_by:raise ValueError('Review attribution required')
  if self.version>1 and self.supersedes is None:raise ValueError('Version update requires explicit supersession')
  if self.supersedes is not None and self.supersedes>=self.version:raise ValueError('Invalid supersession')
  if len(set(self.action_types))!=len(self.action_types) or any(not re.fullmatch(r'[A-Z][A-Z_]{1,63}',a) for a in self.action_types):raise ValueError('Invalid action types')
  p=Path(self.file_path)
  if p.is_absolute() or '..' in p.parts or not str(p).startswith('data/documents/') or p.suffix.lower() not in {'.md','.pdf'}:raise ValueError('Unauthorized source path')
  return self
 @property
 def id(self):return f'ORG:{self.document_id}:{self.version}'
 def checked_path(self,root=ROOT):
  root=Path(root).resolve();p=root/self.file_path
  if any(v.is_symlink() for v in [p,*p.parents] if v!=root.parent):raise SourceError('SOURCE_UNAUTHORIZED')
  if not p.is_file():raise SourceError('SOURCE_UNAVAILABLE')
  if not p.resolve().is_relative_to(root/'data/documents'):raise SourceError('SOURCE_UNAUTHORIZED')
  raw=p.read_bytes()
  if not 0<len(raw)<=1_000_000 or hashlib.sha256(raw).hexdigest()!=self.sha256:raise SourceError('SOURCE_CHECKSUM_MISMATCH')
  if p.suffix=='.md' and injection(raw.decode()):raise SourceError('SOURCE_UNTRUSTED_INSTRUCTIONS')
  return p
 def active(self,at):
  return self.status=='ACTIVE' and timestamp(self.effective_from)<=timestamp(at) and (self.effective_to is None or timestamp(at)<timestamp(self.effective_to))
def injection(text):
 return bool(re.search(r'ignore (?:all |previous |prior )*instructions|(?:system|assistant)\s*:\s*|reveal (?:the )?(?:secret|api key)|<\/?(?:system|context)>|hidden[_ -]truth|answer[_ -]key',text,re.I))
def sources(path=ROOT/'data/documents/b11/manifest.json'):
 data=json.loads(Path(path).read_text())
 if set(data)!={'version','owner_mapping','documents'} or data['version']!=2 or data['owner_mapping']!=OWNERS:raise SourceError('MANIFEST_INVALID')
 result=[Source.model_validate({**v,'action_types':tuple(v['action_types'])}) for v in data['documents']]
 if len(result)>100 or len({v.id for v in result})!=len(result):raise SourceError('MANIFEST_ID_CONFLICT')
 return result

class Citation(BaseModel):
 model_config=ConfigDict(extra='forbid',strict=True,hide_input_in_errors=True)
 source_document_id:str=Field(min_length=1,max_length=40)
 source_version:int=Field(ge=1)
 canonical_document_id:str=Field(min_length=1,max_length=60)
 owner_department_id:str
 source_uri:str=Field(max_length=512)
 content_checksum:str=Field(pattern=r'^[0-9a-f]{64}$')
 quote_excerpt:str=Field(min_length=1,max_length=800)
 passage_location:str=Field(pattern=r'^chunk:[0-9]+:[a-f0-9-]{36}$')
 chunk_sha256:str=Field(pattern=r'^[0-9a-f]{64}$')
 confidence_label:Literal['SOURCE_REVIEWED_SYNTHETIC','PROPOSED','DISPUTED']
 assertion_status:Literal['PROPOSED']='PROPOSED'
 retrieved_at:str
 effective_from:str
 derived_from:str|None=None
 trusted_as_instructions:Literal[False]=False
 @model_validator(mode='after')
 def bound(self):
  if self.canonical_document_id!=f'ORG:{self.source_document_id}:{self.source_version}' or self.owner_department_id not in OWNERS.values():raise ValueError('Citation identity binding')
  timestamp(self.retrieved_at);timestamp(self.effective_from)
  if injection(self.quote_excerpt):raise ValueError('Untrusted instructions')
  return self
