"""Bounded B17 read services; fixed RO query families and explicit public fields."""
import time
from app.api import models as m
from app.graph.repository import PreconditionFailed,NotFound
from app.graph.models import digest
from app.graph.schema import timestamp
from app.services.evidence.reader import Reader
from app.services.operations.auth import Denied
from .reads import Reads
from app.services.activity import activity,checkpoint,selected_paths,trace_key
LIMITATIONS=['Current projection, not a historical snapshot; intervening writes can change later pages','Bounded search; no result does not establish global absence']
class Views:
 def __init__(self,services,actor,token,filters):
  self.s,self.repo,self.actor,self.token,self.f=services,services.repo,actor,token,filters
  self.r=Reads(self.repo,services.ops,services.delivery,services.clock,services.reads.memory)
  # Per-request only; no stale shared authorization or projection cache.
  self.nodes={};self.permissions={};self.edge_cache={}
  original_edges=self.r.edges
  self.r.edges=lambda kind,source=None,target=None:self.edge_cache[(kind,source,target)] if (kind,source,target) in self.edge_cache else original_edges(kind,source,target)
  view=self
  class Snapshot:
   def __getattr__(self,key):return getattr(view.repo,key)
   def get_node(self,id,expected_kind=None):
    n=view.node(id)
    if expected_kind and expected_kind not in n.labels:raise NotFound('RESOURCE_TYPE')
    return n
  self.r.repo=Snapshot()
  from app.graph.analysis.reader import Reader as TemporalReader
  from app.graph.analysis.models import AnalysisRequest,AnalysisLimits
  self.reader=TemporalReader(self.repo,AnalysisRequest(operation='dependencies',ids=('B17-view',),as_of=services.clock()),AnalysisLimits(),{'started':time.perf_counter(),'steps':0,'queries':0})
  if filters.before and timestamp(filters.before)>timestamp(services.clock()):raise ValueError('FUTURE_WINDOW')
 def state(self):
  rows=self.repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.repo_revision,coalesce(m.repo_pending,'')")
  if len(rows)!=1 or rows[0][1]:raise PreconditionFailed('SOURCE_RECOVERY_REQUIRED')
  return rows[0][0]
 def node(self,id):
  if id not in self.nodes:self.nodes[id]=self.repo.get_node(id)
  return self.nodes[id]
 def allowed(self,n):
  if n.id not in self.permissions:self.permissions[n.id]=self.reader.visible(n.properties) and self.r.allowed(n,self.actor,self.token)
  return self.permissions[n.id]
 def require(self,id,kind):return self.r.node(id,kind,self.actor,self.token)
 def prime(self,nodes):
  # Two bounded adjacency batches replace per-incident ownership/link scans.
  # Cache exists for this projection only and is protected by revision readback.
  if not nodes:return
  kinds={'REPORTS','PART_OF','OCCURRED_AT','AFFECTS','MAINTAINED_BY','INVESTIGATES','PRODUCED_PLAN','PROPOSES','INSPECTS','PRODUCED','ESTABLISHES','HAS_EVENT','RESULTED_IN','CONCERNS','LOCATED_AT'}
  ids={n.id for n in nodes}
  rows=self.repo._read('MATCH (s:CivicEntity)-[e]->(t:CivicEntity) WHERE (s.id IN $ids OR t.id IN $ids) AND type(e) IN $kinds RETURN type(e),properties(e),labels(s),properties(s),labels(t),properties(t) ORDER BY e.id LIMIT 5001',{'ids':sorted(ids),'kinds':sorted(kinds)})
  if len(rows)>5000:raise PreconditionFailed('VIEW_ADJACENCY_CAPACITY')
  for kind in kinds:
   for id in ids:
    self.edge_cache[kind,id,None]=[];self.edge_cache[kind,None,id]=[]
  for row in rows:
   e=self.repo._decode_edge_row(row)
   self.nodes.update({n.id:n for n in [self.repo.decode_node(row[2],row[3]),self.repo.decode_node(row[4],row[5])]})
   if not self.reader.visible(e.properties):continue
   for key in [(e.kind,e.source,None),(e.kind,None,e.target)]:
    if key in self.edge_cache:
     self.edge_cache[key].append(e)
     if len(self.edge_cache[key])>100:raise PreconditionFailed('READ_EDGE_LIMIT')
 def candidates(self,kind):
  if kind not in {'Incident','ProblemCluster','Investigation','Approval','WorkOrder','Complaint','Department','InfrastructureAsset'}:raise ValueError('VIEW_FAMILY')
  rows=self.repo._read(f'MATCH (n:{kind}) RETURN labels(n),properties(n) ORDER BY n.id LIMIT 501')
  if len(rows)>500:raise PreconditionFailed('VIEW_CAPACITY')
  nodes=[self.repo.decode_node(*row) for row in rows];self.nodes.update({n.id:n for n in nodes})
  self.prime(nodes)
  assets=[n for n in list(self.nodes.values()) if 'InfrastructureAsset' in n.labels]
  self.prime(assets)
  return [n for n in nodes if self.allowed(n)]
 def issues(self,n):
  if n.kind=='Incident':return {n.properties['issue_type']}
  if n.kind=='Complaint':return {self.node(i).properties['issue_type'] for i in self.r.targets('REPORTS',n.id)}
  if n.kind in {'Investigation','ProblemCluster'}:
   ids=self.r.targets('INVESTIGATES',n.id) if n.kind=='Investigation' else self.r.sources('PART_OF',n.id)
   return {self.node(i).properties['issue_type'] for i in ids if self.node(i).kind=='Incident'}
  if 'InfrastructureAsset' in n.labels:return {self.node(i).properties['issue_type'] for i in self.r.sources('AFFECTS',n.id) if self.allowed(self.node(i))}
  if n.kind=='WorkOrder':
   saved=self.s.ops.store.get('order',n.id);plan=self.s.ops.planning.store.get(saved['binding']['plan_id'])
   return self.issues(self.node(plan['draft']['investigation_id']))
  if n.kind=='Approval':
   saved=self.s.ops.store.get('approval',n.id);plan=self.s.ops.planning.store.get(saved['binding']['plan_id'])
   return self.issues(self.node(plan['draft']['investigation_id']))
  return set()
 def departments(self,n):
  if 'InfrastructureAsset' in n.labels:return set(self.r.ownership_departments(n.id))
  if n.kind=='Department':return {n.id}
  if n.kind=='WorkOrder':return {self.s.ops.store.get('order',n.id)['assignment']['department_id']}
  if n.kind=='Approval':return {a['department_id'] for a in self.s.ops.store.get('approval',n.id)['binding']['assignments']}
  if n.kind in {'Incident','ProblemCluster','Investigation','Complaint'}:
   if n.kind=='Incident':ids=self.r.targets('AFFECTS',n.id)
   elif n.kind=='Complaint':ids=self.r.targets('REPORTS',n.id)
   elif n.kind=='ProblemCluster':ids=self.r.sources('PART_OF',n.id)
   else:ids=[i for i in self.r.targets('INVESTIGATES',n.id) if self.node(i).kind=='Incident']
   return {d for i in ids for d in self.departments(self.node(i))}
  return set()
 def matches(self,n):
  f=self.f;p=n.properties
  if f.issue and f.issue not in self.issues(n):return False
  if f.status and f.status!=p.get('status',p.get('operational_status')):return False
  if f.department_id and f.department_id not in self.departments(n):return False
  at=next((p[k] for k in ['reported_at','started_at','requested_at','created_at'] if k in p),None)
  if f.after and (at is None or timestamp(at)<timestamp(f.after)):return False
  if f.before and (at is None or timestamp(at)>timestamp(f.before)):return False
  return True
 def listing(self,kind):
  rows=[self.r.project(n,self.actor,self.token) for n in self.candidates(kind) if self.matches(n)]
  result=self.r.page(rows,self.f.limit,self.f.cursor);result['limitations']=LIMITATIONS;return result
 def dashboard(self):
  inc=[n for n in self.candidates('Incident') if self.matches(n)];clusters=[n for n in self.candidates('ProblemCluster') if self.matches(n)]
  approvals=[n for n in self.candidates('Approval') if self.matches(n)];orders=[n for n in self.candidates('WorkOrder') if self.matches(n)]
  current=[n for n in inc if n.properties['status']!='ENDED']
  investigations=[n for n in self.candidates('Investigation') if self.matches(n)]
  recurring={issue:sum(n.properties['pattern_type']=='RECURRENT' and issue in self.issues(n) for n in clusters) for issue in ['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']}
  return {'open_clusters':sum(n.properties['status']!='CONTROLLED' for n in clusters),'active_investigations':sum(n.properties['status'] not in {'COMPLETED','CANCELLED'} for n in investigations),'recurrence_counts':recurring,'active_incidents':len(current),'active_clusters':sum(n.properties['status']!='CONTROLLED' for n in clusters),'pending_approvals':sum(n.properties['status']=='PENDING' for n in approvals),'completed_work_orders':sum(n.properties['status']=='COMPLETED' for n in orders),'verified_work_orders':sum(self.r.project(n,self.actor,self.token)['resolution_verified'] for n in orders),'issue_counts':{issue:sum(n.properties['issue_type']==issue for n in current) for issue in ['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']},'graph_revision':self.state(),'as_of':self.s.clock(),'definitions':['Active incidents exclude ENDED; active clusters exclude CONTROLLED','Active investigations exclude COMPLETED and CANCELLED; recurrence counts are recorded RECURRENT clusters per issue, including history','open_clusters aliases active_clusters; neither counts CONTROLLED clusters','Pending approvals have native PENDING status','Completed work is independent of latest evidence-backed RESOLUTION_VERIFIED outcome'],'limitations':LIMITATIONS}
 def hypotheses(self,id):
  self.require(id,'Investigation')
  rows=[self.r.get(i,'Hypothesis',self.actor,self.token) for i in self.r.targets('PROPOSES',id)]
  if self.f.status:rows=[v for v in rows if v['status']==self.f.status]
  return self.r.page(rows,self.f.limit,self.f.cursor)
 def trace(self,id):
  inv=self.r.get(id,'Investigation',self.actor,self.token);items=activity(self.repo,id,self.s.clock())
  items=[v for v in items if (not self.f.after or timestamp(v['timestamp'])>=timestamp(self.f.after)) and (not self.f.before or timestamp(v['timestamp'])<=timestamp(self.f.before)) and (not self.f.status or v['status']==self.f.status)]
  if self.actor.role=='DEPARTMENT_LEAD':
   for v in items:
    v['evidence_ids']=[i for i in v.get('evidence_ids',[]) if self.allowed(self.node(i))]
    v['rationale_summary']=None  # summary text is not proven department-scoped
    v['graph_path_ids']=[]  # path bodies are separately scoped by graph projection
  # Trace pagination uses chronological timestamp+stable ID, unlike resource pages.
  key=trace_key
  if self.f.cursor:
   stamp,sep,event=self.f.cursor.partition('|')
   if not sep or not event or stamp!=timestamp(stamp).strftime('%Y-%m-%dT%H:%M:%S.%fZ'):raise ValueError('TRACE_CURSOR_FORMAT')
  items.sort(key=lambda v:(timestamp(v['timestamp']),v['event_id']))
  eligible=[v for v in items if not self.f.cursor or key(v)>self.f.cursor];page=eligible[:self.f.limit]
  state,quarantined=checkpoint(self.repo,self.s.profile,id)
  import re
  codes=[v if re.fullmatch(r'[A-Z][A-Z0-9_]{0,99}',v) else 'RECORDED_RUNTIME_ERROR' for v in (state.errors if state else [])]
  return {'checkpoint_graph_revision':state.graph_revision if state else None,'refresh_required':bool(state and (state.refresh_required or state.graph_revision!=self.state())),'error_codes':codes,'items':page,'total_count':len(items),'next_cursor':key(page[-1]) if len(eligible)>len(page) and page else None,'graph_revision':self.state(),'as_of':self.s.clock(),'phase':state.phase if state else None,'pause_reason':state.pause_reason if state else None,'recovery_required':quarantined or bool(state and state.pause_reason and 'RECOVERY' in state.pause_reason),'current_agent_role':state.phase if state else None,'active_incident_ids':inv['incident_ids'],'historical_incident_ids':inv['historical_incident_ids'],'limitations':[*LIMITATIONS,'Only persisted public decision summaries and validated broker metadata; raw arguments and private reasoning withheld','Scripted execution modes are test behavior, not genuine live autonomy',*(['No persisted checkpoint available'] if state is None else [])]}
 def asset(self,id):
  n=self.require(id,'InfrastructureAsset');p=n.properties;locations=self.r.targets('LOCATED_AT',id)
  return {'location_id':locations[0] if len(locations)==1 else None,'owner_department_id':self.r.ownership_departments(id,verified_only=True)[0] if len(self.r.ownership_departments(id,verified_only=True))==1 else None,'condition':p.get('condition'),'id':id,'labels':list(n.labels),'asset_type':p['asset_type'],'name':p['name'],'operational_status':p['operational_status'],'department_ids':self.r.ownership_departments(id),'location_ids':locations,'incident_ids':[i for i in self.r.sources('AFFECTS',id) if self.allowed(self.node(i))],'graph_revision':self.state(),'as_of':self.s.clock(),'geometry_status':'LOCATION_REFERENCES' if locations else 'UNAVAILABLE'}
 def graph(self,id,kind):
  root=self.require(id,kind);nodes={id:root};edges={};front=[id];truncated=False
  # Finite breadth-first fixed query. Authorization and temporal checks precede
  # admission to each next frontier; no path through an unauthorized endpoint.
  safe={'INVESTIGATES','PART_OF','REPORTS','AFFECTS','LOCATED_AT','OCCURRED_AT','IN_ZONE','MAINTAINED_BY','DRAINS_TO','SERVES','PROPOSES','CONCERNS','HAS_ASSESSMENT','SUPPORTED_BY','CONTRADICTED_BY','INSPECTS','PRODUCED','ESTABLISHES','ABOUT','PRODUCED_PLAN','HAS_TASK','TARGETS','ASSIGNED_TO','DEPENDS_ON','IMPLEMENTS','HAS_EVENT','RESULTED_IN'}
  for _ in range(self.f.depth):
   if not front:break
   rows=self.repo._read('MATCH (s:CivicEntity)-[e]->(t:CivicEntity) WHERE (s.id IN $ids OR t.id IN $ids) AND type(e) IN $kinds RETURN type(e),properties(e),labels(s),properties(s),labels(t),properties(t) ORDER BY e.id LIMIT 201',{'ids':front,'kinds':sorted(safe)})
   if len(rows)>200:truncated=True
   next_ids=set()
   for row in rows[:200]:
    e=self.repo._decode_edge_row(row)
    if not self.reader.visible(e.properties):continue
    if e.kind in self.repo.policy['verified_associations'] and e.properties.get('association_status')!='VERIFIED' and not self.f.include_candidates:continue
    ends=[self.repo.decode_node(row[2],row[3]),self.repo.decode_node(row[4],row[5])];self.nodes.update({n.id:n for n in ends})
    if not all(self.graph_allowed(n,root) for n in ends):continue
    evidence=e.properties.get('source_evidence_id')
    proof=self.reader._evidence(e)
    if proof is not None and not self.reader.visible(proof.properties):continue
    if self.actor.role=='DEPARTMENT_LEAD' and evidence and not self.allowed(self.node(evidence)):continue
    if len(set(nodes)|{n.id for n in ends})>120 or len(edges)>=200 and e.id not in edges:truncated=True;continue
    for n in ends:
     if n.id not in nodes:next_ids.add(n.id);nodes[n.id]=n
    edges[e.id]=e
   front=sorted(next_ids)
  if any(len({e.properties['source_evidence_id'] for e in edges.values() if n.id in {e.source,e.target} and e.properties.get('source_evidence_id')})>100 for n in nodes.values()):truncated=True
  paths=selected_paths(self.repo,id,activity(self.repo,id,self.s.clock()),set(nodes),edges,self.s.clock()) if kind=='Investigation' else []
  if self.actor.role=='DEPARTMENT_LEAD':paths=[p for p in paths if all(self.allowed(self.node(i)) for i in p['evidence_ids'])]
  return {'decision_paths':paths,'nodes':[self.public_node(n,edges) for n in sorted(nodes.values(),key=lambda n:n.id)],'edges':[self.public_edge(e) for e in sorted(edges.values(),key=lambda e:e.id)],'decision_path_ids':[p['id'] for p in paths],'graph_revision':self.state(),'as_of':self.s.clock(),'truncated':truncated,'reservations':[*LIMITATIONS,'Neighborhood connections are context, not proof of physical causation','Candidate associations excluded' if not self.f.include_candidates else 'Candidate associations explicitly requested; never verified causation','Only persisted decision path bodies whose endpoints remain visible in this bounded projection are highlighted']}
 def graph_allowed(self,n,root):
  if not self.reader.visible(n.properties):return False
  if self.actor.role!='DEPARTMENT_LEAD':return True
  # Do not project generic connected records on department scope alone. Only
  # resources already covered by the accepted resource authorization are visible.
  return self.allowed(n)
 def public_node(self,n,edges):
  p=n.properties;ev=sorted({e.properties['source_evidence_id'] for e in edges.values() if (e.source==n.id or e.target==n.id) and e.properties.get('source_evidence_id')})
  return {'id':n.id,'labels':list(n.labels),'kind':n.kind,'display_label':str(p.get('name',p.get('title',n.id)))[:512],'status':p.get('status',p.get('operational_status',p.get('verification_status'))),'source_kind':p.get('source_kind'),'evidence_ids':ev[:100],'observed_at':p.get('observed_at')}
 def public_edge(self,e):
  p=e.properties
  return {'id':e.id,'type':e.kind,'source':e.source,'target':e.target,'valid_from':p.get('valid_from'),'valid_to':p.get('valid_to'),'observed_at':p.get('observed_at'),'verification_status':p.get('association_status',p.get('verification_status','RECORDED_ASSOCIATION_NOT_CAUSATION')),'source_evidence_ids':[p['source_evidence_id']] if p.get('source_evidence_id') else []}
 def map(self):
  features={};unavailable=[]
  inc=[n for n in self.candidates('Incident') if self.matches(n)]
  assets=[n for n in self.candidates('InfrastructureAsset') if self.matches(n)]
  if self.f.investigation_id:
   self.require(self.f.investigation_id,'Investigation');ids=set(self.r.targets('INVESTIGATES',self.f.investigation_id));inc=[n for n in inc if n.id in ids];aids={a for n in inc for a in self.r.targets('AFFECTS',n.id)};assets=[n for n in assets if n.id in aids]
  for n in [*inc,*assets]:
   locations=self.r.targets('OCCURRED_AT' if n.kind=='Incident' else 'LOCATED_AT',n.id)
   if not locations:unavailable.append(n.id)
   for lid in locations:
    loc=self.node(lid);p=loc.properties
    if not self.reader.visible(p):unavailable.append(n.id);continue
    lon,lat=p.get('longitude'),p.get('latitude')
    if type(lon) not in {float,int} or type(lat) not in {float,int} or not -180<=lon<=180 or not -90<=lat<=90:unavailable.append(n.id);continue
    feature=features.setdefault(lid,{'id':lid,'location_id':lid,'geometry':{'coordinates':[float(lon),float(lat)]},'issue_types':[],'asset_ids':[],'incident_ids':[],'investigation_ids':[]})
    feature['issue_types']=sorted(set(feature['issue_types'])|self.issues(n))
    feature['incident_ids' if n.kind=='Incident' else 'asset_ids'].append(n.id)
    if n.kind=='Incident':feature['investigation_ids']=sorted(set(feature['investigation_ids'])|{i for i in self.r.sources('INVESTIGATES',n.id) if self.allowed(self.node(i))})
  page=self.r.page(list(features.values()),self.f.limit,self.f.cursor)
  return {'features':page['items'],'unavailable_ids':sorted(set(unavailable)),'next_cursor':page['next_cursor'],'total_count':page['total_count'],'graph_revision':self.state(),'as_of':self.s.clock(),'truncated':page['next_cursor'] is not None,'limitations':[*LIMITATIONS,'Only canonical numeric Location points; geometry artifacts are not inferred or loaded']}
 def run(self,name,id=None):
  before=self.state()
  if name.startswith('list:'):out=self.listing(name.split(':')[1])
  elif name=='dashboard':out=self.dashboard()
  elif name=='map':out=self.map()
  elif name=='asset':out=self.asset(id)
  elif name=='neighbors':out=self.graph(id,'InfrastructureAsset')
  elif name=='graph':out=self.graph(id,'Investigation')
  elif name=='trace':out=self.trace(id)
  elif name=='hypotheses':out=self.hypotheses(id)
  else:raise ValueError('VIEW_FAMILY')
  if before!=self.state():raise PreconditionFailed('PROJECTION_CHANGED_REFETCH')
  return out
