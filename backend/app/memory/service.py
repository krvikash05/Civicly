"""Source-first reconciliation and bounded cited retrieval, no generated claims."""
import asyncio,hashlib
from .models import SourceError,ROOT,injection,Citation
from app.graph.schema import timestamp,utc_now
from .sdk import SDK
from .storage import Store
class Memory:
 def __init__(self,repo,config,*,root=ROOT):self.store=Store(repo);self.repo=repo;self.config=config;self.root=root
 async def ingest(self,source,*,interrupt=None):
  lock=self.repo.client.connection.lock('civicly:document-ingest:'+self.repo.graph.name+':'+self.config.graph_name,timeout=60,blocking=False)
  if not lock.acquire():raise SourceError('INGEST_BUSY')
  try:
   async with asyncio.timeout(30):return await self._ingest(source,interrupt=interrupt,ingest_lock=lock)
  finally:
   if lock.owned():lock.release()
 async def _ingest(self,source,*,interrupt=None,ingest_lock=None):
  path=source.checked_path(self.root);self.store.journal(source,'STAGED')
  sdk=SDK(self.config)
  try:
   old=self.store.get(source.id)
   if old:
    if old[0]!=source or old[2]!=self.config.graph_name:raise SourceError('DOCUMENT_VERSION_CONFLICT')
    if await sdk.chunks(source.id)!=old[1]:raise SourceError('SDK_INTEGRITY')
    await sdk.validate_indexing(source.id,old[1])
    self.store.ensure_procedure(source)
    self.store.journal(source,'READY')
    return {'id':source.id,'replayed':True,'chunks':old[1]}
   # Lexical graphs may exist after interruption. Verify content on retry then
   # reuse; incomplete extraction/indexing reruns SDK ingestion using update.
   result=await sdk.ingest(path,source.id)
   chunks=await sdk.chunks(source.id)
   if any(injection(c['text']) for c in chunks):raise SourceError('SOURCE_UNTRUSTED_INSTRUCTIONS')
   self.store.journal(source,'INDEXED')
   if interrupt=='after_sdk':raise SourceError('INJECTED_AFTER_SDK')
   if not ingest_lock.owned():raise SourceError('INGEST_LEASE_LOST')
   self.store.register(source,chunks,self.config.graph_name)
   if interrupt=='after_registration':raise SourceError('INJECTED_AFTER_REGISTRATION')
   self.store.journal(source,'READY')
   return {'id':source.id,'replayed':False,'chunks':chunks,'sdk':result.model_dump(mode='json')}
  finally:await sdk.close()
 async def retrieve(self,*,as_of,document_id=None,version=None,department_id=None,action_type=None,include_candidates=False):
  before=self.repo._read("MATCH (m:CivicSchemaMigration {id:$id}) RETURN m.repo_revision,coalesce(m.repo_pending,'') LIMIT 1",{'id':'0001'})
  if not before or before[0][1]:raise SourceError('MEMORY_REVISION_PENDING')
  all_sources=self.store.all();candidates=[];gaps=[]
  for item in all_sources:
   source,chunks,graph=item
   if graph!=self.config.graph_name:raise SourceError('SDK_SCOPE_MISMATCH')
   if document_id and source.document_id!=document_id or version and source.version!=version or department_id and source.owner_department_id!=department_id or action_type and action_type not in source.action_types:continue
   if not source.active(as_of):gaps.append('SOURCE_REVOKED_OR_OUTSIDE_VALIDITY');continue
   # Select current version at requested effective cutoff, preserving originals.
   if any(v[0].document_id==source.document_id and v[0].version>source.version and timestamp(v[0].effective_from)<=timestamp(as_of) for v in all_sources):
    gaps.append('SOURCE_SUPERSEDED');continue
   if source.review_status!='REVIEWED' and not include_candidates:gaps.append('SOURCE_NOT_REVIEWED');continue
   try:source.checked_path(self.root)
   except SourceError as e:gaps.append(str(e));continue
   candidates.append(item)
  if not candidates:return {'status':'UNAVAILABLE','citations':[],'gaps':sorted(set(gaps or ['SOURCE_UNAVAILABLE'])),'truncated':False}
  if len(candidates)>20:return {'status':'PARTIAL','citations':[],'gaps':['SOURCE_SELECTION_LIMIT; narrow source/owner'],'truncated':True}
  sdk=SDK(self.config,readonly=True)
  try:
   result=await sdk.retrieve(action_type or candidates[0][0].title)
   matching={item.metadata['chunk_id']:item for item in result.items}
   citations=[]
   for source,expected,graph in candidates:
    actual=await sdk.chunks(source.id)
    if actual!=expected:raise SourceError('SDK_INTEGRITY')
    await sdk.validate_indexing(source.id,actual)
    for c in actual:
     # Eligibility was established before this bounded source-chunk fallback.
     # Read evidence from the actual SDK graph; metadata alone is insufficient.
     if document_id is None and c['id'] not in matching:
      gaps.append('ELIGIBLE_SOURCE_FALLBACK; verified source chunks outside global top12; applicability, not semantic ranking')
     if injection(c['text']):raise SourceError('SOURCE_UNTRUSTED_INSTRUCTIONS')
     citations.append({'source_document_id':source.document_id,'source_version':source.version,'canonical_document_id':source.id,'owner_department_id':source.owner_department_id,'source_uri':source.file_path,'content_checksum':source.sha256,'quote_excerpt':c['text'][:800],'passage_location':f'chunk:{c["index"]}:{c["id"]}','chunk_sha256':c['sha256'],'confidence_label':'SOURCE_REVIEWED_SYNTHETIC' if source.review_status=='REVIEWED' else source.review_status,'assertion_status':'PROPOSED','retrieved_at':utc_now(),'effective_from':source.effective_from,'derived_from':source.derived_from,'trusted_as_instructions':False})
   citations=[Citation.model_validate(c).model_dump(mode='json') for c in citations]
   after=self.repo._read("MATCH (m:CivicSchemaMigration {id:$id}) RETURN m.repo_revision,coalesce(m.repo_pending,'') LIMIT 1",{'id':'0001'})
   if before!=after:raise SourceError('MEMORY_REVISION_CHANGED')
   if not citations:gaps.append('INDEXED_SOURCE_OUTSIDE_BOUNDED_RETRIEVAL; not proof of source absence')
   conflict=len({s.review_status for s,_,_ in candidates})>1 or any(s.review_status=='DISPUTED' for s,_,_ in candidates)
   return {'status':'PARTIAL' if conflict or gaps or len(citations)>5 else 'SUCCESS' if citations else 'UNAVAILABLE','citations':citations[:5],'gaps':sorted(set(gaps+(['SOURCE_CONFLICT_OR_DISPUTE; no authoritative resolution'] if conflict else [])+['Synthetic source excerpts; extracted statements remain PROPOSED, not verified policy or physical cause'])),'truncated':len(citations)>5}
  finally:await sdk.close()
