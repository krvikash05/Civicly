"""Actual SDK1.4.0 strategies with narrow6.0.2 DDL adaptation and RO retrieval."""
import hashlib,math,re
from graphrag_sdk import GraphRAG,ConnectionConfig,FalkorDBConnection,GraphStore,VectorStore,Embedder,LLMInterface,FixedSizeChunking,Ontology,Entity
from graphrag_sdk.core.models import GraphData,GraphNode,LLMResponse,IngestionResult
from graphrag_sdk.ingestion.extraction_strategies.base import ExtractionStrategy
from graphrag_sdk.retrieval.strategies.local import LocalRetrieval
from .models import injection,SourceError
DDL={"CALL db.idx.fulltext.createNodeIndex('Chunk', 'text')":"CREATE FULLTEXT INDEX FOR (n:Chunk) ON (n.text)","CALL db.idx.fulltext.createNodeIndex('__Entity__', 'name', 'description')":"CREATE FULLTEXT INDEX FOR (n:__Entity__) ON (n.name,n.description)"}
def docs_target(name):
 from app.graph.targets import is_disposable_graph
 if name!='civicly_docs' and not (name.startswith('civicly_docs_b11_test_') and is_disposable_graph(name.replace('civicly_docs_b11_test_','civicly_b11_test_'))):raise ValueError('Unauthorized SDK graph')
 return name
class Connection(FalkorDBConnection):
 def __init__(self,config,*,readonly=False):docs_target(config.graph_name);super().__init__(config);self.readonly=readonly
 async def query(self,cypher,params=None,*,timeout=None):
  if self.readonly:
   self._ensure_client()
   return await self._graph.ro_query(cypher,params=params,timeout=min(timeout or 1000,3000))
  return await super().query(DDL.get(cypher,cypher),params,timeout=timeout)
class OfflineEmbedder(Embedder):
 """Deterministic lexical hashing; offline baseline, not learned semantic accuracy."""
 @property
 def model_name(self):return 'civicly-offline-lexical-hash64-v1'
 def embed_query(self,text,**kwargs):
  v=[0.0]*64
  for word in re.findall(r'[a-z]{2,}',text.lower()):v[int.from_bytes(hashlib.sha256(word.encode()).digest()[:4],'big')%64]+=1
  norm=math.sqrt(sum(x*x for x in v)) or 1
  return [x/norm for x in v]
class NoLLM(LLMInterface):
 def __init__(self):super().__init__('OFFLINE_NO_LLM_AUTHORITY')
 def invoke(self,prompt,**kwargs):raise SourceError('LLM_NOT_AUTHORIZED')
class SourceExtraction(ExtractionStrategy):
 """Lossless source statements, proposed only; never extracts verified policies."""
 async def extract(self,chunks,ontology,ctx):
  nodes=[]
  for c in chunks.chunks:
   if injection(c.text):raise SourceError('SOURCE_UNTRUSTED_INSTRUCTIONS')
   nodes.append(GraphNode(id='statement:'+c.uid,label='SourceStatement',properties={'name':c.uid,'description':c.text,'assertion_status':'PROPOSED','source_chunk_ids':[c.uid]}))
  return GraphData(nodes=nodes)
class SDK:
 def __init__(self,config,*,readonly=False):
  self.conn=Connection(config,readonly=readonly);self.embedder=OfflineEmbedder()
  self.graph=GraphStore(self.conn);self.vector=VectorStore(self.conn,self.embedder,embedding_dimension=64)
  self.rag=GraphRAG(self.conn,NoLLM(),self.embedder,ontology=Ontology(entities=[Entity(label='SourceStatement',description='Untrusted cited source text; PROPOSED only')]),embedding_dimension=64)
 async def close(self):await self.rag.close()
 async def ingest(self,path,id):
  from graphrag_sdk.ingestion.loaders.markdown_loader import MarkdownLoader
  from graphrag_sdk.ingestion.loaders.pdf_loader import PdfLoader
  from graphrag_sdk.core.context import Context
  loader=MarkdownLoader() if path.suffix=='.md' else PdfLoader()
  loaded=await loader.load(str(path),Context())
  if len(loaded.text)>128*800:raise SourceError('SOURCE_CHUNK_BUDGET')
  if injection(loaded.text):raise SourceError('SOURCE_UNTRUSTED_INSTRUCTIONS')
  existing=await self.conn.query('MATCH (d:Document {id:$id}) RETURN d.content_hash LIMIT 2',{'id':id})
  if existing.result_set:
   chunks=await self.chunks(id)
   if existing.result_set!=[[hashlib.sha256(loaded.text.encode()).hexdigest()]] or ''.join(c['text'] for c in chunks)!=loaded.text:raise SourceError('SDK_PARTIAL_REQUIRES_REPAIR')
   await self.validate_indexing(id,chunks)
   return IngestionResult(chunks_indexed=len(chunks))
  result=await self.rag.ingest(str(path),document_id=id,chunker=FixedSizeChunking(800,0),extractor=SourceExtraction())
  if result.chunks_indexed<1:raise SourceError('SDK_NO_INDEXED_CHUNKS')
  # No LLM-based finalize: exact-source IDs need no fuzzy entity merge. SDK
  # ingestion already creates lexical/mention graph, chunk vectors and indices.
  await self.validate_indexing(id,await self.chunks(id))
  return result
 async def validate_indexing(self,id,chunks):
  """Observable required state only; not proof of internal ANN membership."""
  try:
   indices=await self.conn.query('CALL db.indexes() YIELD label,properties,types,status,options RETURN label,properties,types,status,options')
   ready=False
   for label,properties,types,status,options in indices.result_set:
    if label!='Chunk' or status!='OPERATIONAL':continue
    opts=options.get('embedding',{})
    ready=ready or ('VECTOR' in types.get('embedding',[]) and 'FULLTEXT' in types.get('text',[]) and opts.get('dimension')==64 and opts.get('similarityFunction')=='cosine')
   if not ready:raise ValueError('Required index not operational')
   rows=await self.conn.query('MATCH (:Document {id:$id})-[:PART_OF]->(c:Chunk) RETURN c.id,c.embedding ORDER BY c.index,c.id LIMIT 129',{'id':id})
   if len(rows.result_set)!=len(chunks):raise ValueError('Vector cardinality')
   for (chunk_id,vector),chunk in zip(rows.result_set,chunks):
    expected=self.embedder.embed_query(chunk['text'])
    if chunk_id!=chunk['id'] or not isinstance(vector,list) or len(vector)!=64 or not any(expected):raise ValueError('Vector shape')
    if any(type(v) not in (float,int) or not math.isfinite(v) or not math.isclose(v,e,rel_tol=1e-6,abs_tol=1e-7) for v,e in zip(vector,expected)):raise ValueError('Vector value')
  except Exception as error:
   raise SourceError('SDK_PARTIAL_REQUIRES_REPAIR') from error
 async def retrieve(self,query):
  # Public supported SDK strategy API; no GraphRAG.retrieve config/ontology writes
  # and no unrestricted default generated Cypher on a runtime read credential.
  strategy=LocalRetrieval(self.graph,self.vector,self.embedder,top_k=12,include_entities=False)
  return await strategy.search(query)
 async def chunks(self,id):
  result=await self.conn.query('MATCH (d:Document {id:$id})-[:PART_OF]->(c:Chunk) RETURN c.id,c.text,c.index ORDER BY c.index,c.id LIMIT 129',{'id':id})
  if not result.result_set or len(result.result_set)>128:raise SourceError('SDK_CHUNK_BOUNDARY')
  return [{'id':i,'text':t,'index':n,'sha256':hashlib.sha256(t.encode()).hexdigest()} for i,t,n in result.result_set]
