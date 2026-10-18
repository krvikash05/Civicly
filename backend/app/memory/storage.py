"""Compatible additive0003 and controlled cross-graph registration journal."""
import hashlib,json
from pathlib import Path
from app.graph.migration import MigrationRunner,MigrationError
from app.graph.repository import GraphRepository,Conflict,NotFound
from app.graph.schema import utc_now,timestamp
from app.graph.models import digest
from .models import Source,SourceError
PLAN=Path(__file__).resolve().parents[1]/'graph/migrations/0003_document_memory.json'
class MemoryMigration:
 def __init__(self,client,name):
  self.base=MigrationRunner(client,name);self.graph=self.base.graph;self.client=client
  self.plan=json.loads(PLAN.read_text());self.checksum=hashlib.sha256(PLAN.read_bytes()).hexdigest()
  if self.base.checksum!=self.plan['requires_0001_sha256']:raise MigrationError('0001 mismatch')
 def status(self):
  rows=self.graph.ro_query('MATCH (m:CivicDocumentMigration {id:$id}) RETURN m.checksum,m.state LIMIT 2',params={'id':'0003'}).result_set
  if len(rows)>1 or rows and (rows[0][0]!=self.checksum or rows[0][1] not in {'APPLYING','FAILED','READY'}):raise MigrationError('0003 checksum/state mismatch')
  ready=bool(rows and rows[0][1]=='READY')
  if ready:
   for k in ['indexes','constraints']:
    for spec in self.plan[k]:self.base._wait(k,spec,.1)
  return {'id':'0003','ready':ready,'checksum':self.checksum}
 def apply(self,retry_failed=False):
  if not self.base.status()['ready']:raise MigrationError('0001 not READY')
  lock=self.client.connection.lock('civicly:memory-migration:'+self.graph.name,timeout=30,blocking_timeout=1)
  if not lock.acquire():raise MigrationError('Migration busy')
  def state(s):self.graph.query('MERGE (m:CivicDocumentMigration {id:$id}) SET m.checksum=$sha,m.state=$state,m.updated_at=$at',params={'id':'0003','sha':self.checksum,'state':s,'at':utc_now()})
  try:
   if self.status()['ready']:return self.status()
   state('APPLYING')
   for spec in self.plan['indexes']:self.base._ensure_index(spec)
   for spec in self.plan['constraints']:self.base._ensure_constraint(spec,retry_failed)
   state('READY');return self.status()
  except Exception:state('FAILED');raise
  finally:lock.release()
class Store:
 def __init__(self,repo):
  self.repo=repo
  if not MemoryMigration(repo.client,repo.graph.name).status()['ready']:raise MigrationError('Memory not READY')
 def get(self,id):
  rows=self.repo._read('MATCH (d:Document {id:$id}),(v:CivicDocumentVersion {id:$id}) WHERE v.state=$state RETURN properties(d),properties(v) LIMIT 2',{'id':id,'state':'READY'})
  if not rows:return None
  if len(rows)!=1:raise SourceError('DOCUMENT_CONFLICT')
  props,v=rows[0];self.repo.registry.validate_node('Document',props)
  source=Source.model_validate_json(v['payload_json'])
  if source.id!=id or digest(source.model_dump(mode='json'))!=v['payload_sha256'] or props['content_hash']!=source.sha256 or props['content_ref']!=f"{v['docs_graph']}/{source.id}" or props['source_uri']!=source.file_path or props['title']!=source.title:raise SourceError('DOCUMENT_INTEGRITY')
  return source,json.loads(v['chunks_json']),v['docs_graph']
 def all(self):
  rows=self.repo._read("MATCH (v:CivicDocumentVersion) WHERE v.state='READY' RETURN v.id ORDER BY v.id LIMIT 101")
  if len(rows)>100:raise SourceError('DOCUMENT_BUDGET')
  return [self.get(row[0]) for row in rows]
 def journal(self,source,phase):
  if phase not in {'STAGED','INDEXED','READY','REVOKED'}:raise SourceError('JOURNAL_PHASE')
  self.repo.graph.query('MERGE (j:CivicDocumentJournal {id:$id}) SET j.phase=$phase,j.events=coalesce(j.events,[])+$event,j.updated_at=$at',params={'id':source.id,'phase':phase,'event':[json.dumps({'phase':phase,'source_hash':source.sha256,'at':utc_now()})],'at':utc_now()},timeout=1000)
 def procedure(self,source):
  now=utc_now()
  return {'id':f'ORGPROC:{source.document_id}:{source.version}','schema_version':3,'municipality_id':'demo-city','created_at':now,'updated_at':now,'title':source.title,'version':str(source.version),'status':'PROPOSED','valid_from':source.effective_from,'document_ref':source.id}
 def ensure_procedure(self,source):
  props=self.procedure(source)
  try:
   n=self.repo.get_node(props['id'],'KnowledgeProcedure')
   if any(n.properties[k]!=props[k] for k in ['document_ref','version','status','title','valid_from']):raise SourceError('PROCEDURE_BINDING')
   return n.id
  except NotFound:
   return self.repo.create_node('KnowledgeProcedure',props).id
 def register(self,source,chunks,docs_graph):
  raw=source.model_dump_json();sha=digest(source.model_dump(mode='json'));now=utc_now()
  with self.repo._session() as session:
   old=self.get(source.id)
   if old:
    if old!=(source,chunks,docs_graph):raise Conflict('Document version immutable; use new version')
    return source.id
   self.repo.get_node(source.owner_department_id,'Department')
   versions=[s.version for s,_,_ in self.all() if s.document_id==source.document_id]
   if versions and source.supersedes!=max(versions):raise SourceError('SUPERSESSION_INVALID')
   if source.supersedes:
    previous=self.get(f'ORG:{source.document_id}:{source.supersedes}')
    if previous is None or previous[0].owner_department_id!=source.owner_department_id or timestamp(previous[0].effective_from)>=timestamp(source.effective_from):raise SourceError('SUPERSESSION_INVALID')
   props={'id':source.id,'schema_version':3,'municipality_id':'demo-city','created_at':now,'updated_at':now,'document_type':'ORGANIZATIONAL_SYNTHETIC','title':source.title,'source_uri':source.file_path,'content_hash':source.sha256,'content_ref':f'{docs_graph}/{source.id}'}
   self.repo.registry.validate_node('Document',props)
   detail={'id':source.id,'payload_json':raw,'payload_sha256':sha,'state':'READY','chunks_json':json.dumps(chunks),'docs_graph':docs_graph,'history_json':[]} 
   procedure=self.procedure(source);self.repo.registry.validate_node('KnowledgeProcedure',procedure)
   self.repo._commit(session,'node',source.id,'','CREATE (n:CivicEntity:Document) SET n=$props CREATE (p:CivicEntity:KnowledgeProcedure) SET p=$procedure CREATE (v:CivicDocumentVersion) SET v=$detail',{'props':props,'detail':detail,'procedure':procedure},'n')
  return source.id
 def revoke(self,id,*,operator,reason):
  if not operator.strip() or not reason.strip():raise SourceError('REVOCATION_ATTRIBUTION')
  old=self.get(id)
  if old is None:raise SourceError('SOURCE_UNAVAILABLE')
  source,chunks,graph=old
  if source.status=='REVOKED':return id
  new=Source.model_validate({**source.model_dump(),'status':'REVOKED'})
  with self.repo._session() as session:
   node=self.repo.get_node(id,'Document')
   self.repo._commit(session,'node',id,node.content_hash,'MATCH (n:Document {id:$id}),(v:CivicDocumentVersion {id:$id}) SET v.payload_json=$raw,v.payload_sha256=$sha,v.history_json=coalesce(v.history_json,[])+$history,n.updated_at=$at',{'id':id,'history':[json.dumps({'operator':operator,'reason':reason,'previous':source.model_dump(mode='json'),'at':utc_now()})],'raw':new.model_dump_json(),'sha':digest(new.model_dump(mode='json')),'at':utc_now()},'n')
  self.journal(new,'REVOKED');return id
