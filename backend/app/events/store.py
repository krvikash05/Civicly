"""Delivery companions through existing short fence and an immutable intent marker."""
import json
from uuid import uuid4
from app.active import is_shared_target
from app.graph.models import digest
from app.graph.repository import PreconditionFailed
from app.services.operations.storage import Storage
from app.services.operations.migration import OperationsMigration

class Store(Storage):
 def __init__(self,repo,clock):
  super().__init__(repo);self.clock=clock
  if not is_shared_target(repo.graph.name) or not OperationsMigration(repo.client,repo.graph.name).status()['ready']:raise PreconditionFailed('DELIVERY_EXACT_PROFILE_AND_0005_REQUIRED')
 def rows(self,kind,limit=500):
  rows=self.repo._read('MATCH (s:CivicOperationState {kind:$kind}) RETURN s.id,s.payload_json,s.payload_sha256 ORDER BY s.id LIMIT $limit',{'kind':kind,'limit':limit+1})
  if len(rows)>limit:raise PreconditionFailed('DELIVERY_SCAN_BOUND_RECONCILIATION_REQUIRED')
  out=[]
  for _,raw,sha in rows:
   value=json.loads(raw)
   if digest(value)!=sha:raise PreconditionFailed('DELIVERY_INTEGRITY')
   out.append(value)
  return out
 def write(self,session,states,*,nodes=None,updates=None):
  at=self.clock();id='EV-B15-AUDIT-'+uuid4().hex
  marker={'id':id,'schema_version':3,'municipality_id':'demo-city','created_at':at,'updated_at':at,'recorded_at':at,'source_kind':'SYNTHETIC','source_record_id':id,'evidence_type':'B15_DELIVERY_AUDIT','reliability':'UNVERIFIED','summary':json.dumps({'transition_hash':digest(states),'keys':[kind+':'+key for kind,key,_ in states]},sort_keys=True)}
  self.commit(session,id,[('Evidence',marker),*(nodes or [])],updates or [],[],states)
