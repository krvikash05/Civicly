"""Bounded explicit projections; no raw journals, arbitrary queries or hidden totals."""
from app.api import models as m
from app.graph.repository import PreconditionFailed,NotFound
from app.graph.models import digest
from app.graph.schema import timestamp
from app.services.evidence.reader import Reader
from app.services.evidence.service import EvidenceService
from app.services.operations.auth import Denied
from app.services.planning.models import PlanDraft,PlanReceipt
class Reads:
 def __init__(self,repo,ops,delivery,clock,memory=None):self.repo,self.ops,self.delivery,self.clock,self.memory=repo,ops,delivery,clock,memory
 def ids(self,kind):
  if kind not in {'Complaint','Incident','ProblemCluster','Investigation','Evidence','Inspection','ResolutionPlan','Approval','WorkOrder','Department','InterventionOutcome','Hypothesis'}:raise ValueError('READ_FAMILY')
  rows=self.repo._read(f'MATCH (n:{kind}) RETURN n.id ORDER BY n.id LIMIT 501')
  if len(rows)>500:raise PreconditionFailed('READ_SCAN_LIMIT')
  return [r[0] for r in rows]
 def edges(self,kind,source=None,target=None):
  if kind not in {'REPORTS','PART_OF','OCCURRED_AT','AFFECTS','MAINTAINED_BY','INVESTIGATES','PRODUCED_PLAN','PROPOSES','INSPECTS','PRODUCED','ESTABLISHES','HAS_EVENT','RESULTED_IN','CONCERNS','LOCATED_AT'}:raise ValueError('READ_EDGE_FAMILY')
  reader=Reader(self.repo,self.clock())
  raw=self.repo._read(f'MATCH (s:CivicEntity)-[e:{kind}]->(t:CivicEntity) WHERE ($source IS NULL OR s.id=$source) AND ($target IS NULL OR t.id=$target) RETURN type(e),properties(e),labels(s),properties(s),labels(t),properties(t) ORDER BY e.id LIMIT 101',{'source':source,'target':target})
  if len(raw)>100:raise PreconditionFailed('READ_EDGE_LIMIT')
  rows=[e for row in raw if reader.visible((e:=self.repo._decode_edge_row(row)).properties)]
  if len(rows)>100:raise PreconditionFailed('READ_EDGE_LIMIT')
  return rows
 def targets(self,kind,id):return [e.target for e in self.edges(kind,source=id)]
 def sources(self,kind,id):return [e.source for e in self.edges(kind,target=id)]
 def ownership_departments(self,id,*,verified_only=False):
  edges=self.edges('MAINTAINED_BY',source=id)
  verified=[e for e in edges if e.properties.get('association_status')=='VERIFIED']
  if verified:
   if len(verified)!=1:return [] # Conflict is not resolved by target deduplication.
   self.repo._check_evidence(verified[0].properties)
   Reader(self.repo,self.clock()).node(verified[0].properties['source_evidence_id'],'Evidence')
   return [verified[0].target]
  return [] if verified_only else sorted({e.target for e in edges})
 def allowed(self,n,actor,token):
  if actor.role!='DEPARTMENT_LEAD':return True
  k=n.kind;p=n.properties
  if 'InfrastructureAsset' in n.labels:return self.ownership_departments(n.id)==[actor.department_id]
  if k=='Location':
   ids=self.sources('LOCATED_AT',n.id)+self.sources('OCCURRED_AT',n.id)
   return bool(ids) and all(self.allowed(self.repo.get_node(i),actor,token) for i in ids)
  if k=='Department':return n.id==actor.department_id
  if k=='WorkOrder':
   try:self.ops.read_work_order(n.id,token=token);return True
   except Denied:return False
  if k=='ResolutionPlan':
   saved=self.ops.planning.store.get(n.id)
   return bool(saved and all(t['department_id']==actor.department_id for t in saved['draft']['tasks']))
  if k=='Inspection':
   scope,_=EvidenceService(self.repo,clock=self.clock).inspection_source(Reader(self.repo,self.clock()),n.id)
   return scope['department_id']==actor.department_id
  if k=='Evidence':
   if p['evidence_type']=='SERVICE_EXECUTION_SOURCE':
    from app.services.service_evidence import parse_source,validate
    origin=parse_source(p);record=validate(self.repo,origin.report_evidence_id,self.clock())
    return bool(record and record.department_id==actor.department_id and self.allowed(self.repo.get_node(record.report_evidence_id,'Evidence'),actor,token))
   inspections=self.sources('PRODUCED',n.id)
   return bool(inspections) and all(self.allowed(self.repo.get_node(i,'Inspection'),actor,token) for i in inspections)
  if k=='Complaint':
   ids=self.targets('REPORTS',n.id);return bool(ids) and all(self.allowed(self.repo.get_node(i,'Incident'),actor,token) for i in ids)
  if k=='Incident':
   assets=self.targets('AFFECTS',n.id);return bool(assets) and all(self.ownership_departments(i)==[actor.department_id] for i in assets)
  if k=='ProblemCluster':
   ids=self.sources('PART_OF',n.id);return bool(ids) and all(self.allowed(self.repo.get_node(i,'Incident'),actor,token) for i in ids)
  if k=='Hypothesis':
   ids=self.sources('PROPOSES',n.id);return bool(ids) and all(self.allowed(self.repo.get_node(i,'Investigation'),actor,token) for i in ids)
  if k=='Investigation':
   ids=[i for i in self.targets('INVESTIGATES',n.id) if self.repo.get_node(i).kind=='Incident'];return bool(ids) and all(self.allowed(self.repo.get_node(i,'Incident'),actor,token) for i in ids)
  return False
 def node(self,id,kind,actor,token):
  try:n=self.repo.get_node(id,kind)
  except NotFound:
   if actor.role=='DEPARTMENT_LEAD':raise Denied('RESOURCE_SCOPE_DENIED') from None
   raise
  if not Reader(self.repo,self.clock()).visible(n.properties):raise NotFound('RESOURCE_NOT_VISIBLE')
  if not self.allowed(n,actor,token):raise Denied('RESOURCE_SCOPE_DENIED')
  return n
 def page(self,items,limit=25,cursor=None):
  if not 1<=limit<=50:raise ValueError('LIST_LIMIT')
  items=sorted(items,key=lambda x:str(x.get('id',x.get('plan_id',x.get('problem_cluster_id','')))))
  key=lambda x:str(x.get('id',x.get('plan_id',x.get('problem_cluster_id',''))))
  eligible=[x for x in items if cursor is None or key(x)>cursor];page=eligible[:limit]
  return {'items':page,'total_count':len(items),'next_cursor':key(page[-1]) if len(eligible)>limit and page else None}
 def list(self,kind,actor,token,limit,cursor):
  # Scope checked before projection/count/pagination. No unauthorized total exposed.
  rows=[]
  for id in self.ids(kind):
   n=self.repo.get_node(id,kind)
   if Reader(self.repo,self.clock()).visible(n.properties) and self.allowed(n,actor,token):rows.append(self.project(n,actor,token))
  return self.page(rows,limit,cursor)
 def get(self,id,kind,actor,token):return self.project(self.node(id,kind,actor,token),actor,token)
 def project(self,n,actor,token):
  id=n.id;p=n.properties;k=n.kind;base={'id':id,'expected_hash':n.content_hash,'simulated':True}
  if k=='Complaint':
   inc=self.targets('REPORTS',id);issue=self.repo.get_node(inc[0],'Incident').properties['issue_type'] if inc else 'UNAVAILABLE'
   return {**base,'description':p['description'],'incident_id':inc[0] if len(inc)==1 else None,'reported_at':p['reported_at'],'source_kind':p['source_kind'],'status':p['status'],'issue_type':issue}
  if k=='Incident':
   clusters=self.targets('PART_OF',id);locations=self.targets('OCCURRED_AT',id)
   return {**base,**{f:p.get(f) for f in ['issue_type','subtype','started_at','ended_at','status']},'location_id':locations[0] if len(locations)==1 else None,'cluster_id':clusters[0] if len(clusters)==1 else None,'complaint_ids':self.sources('REPORTS',id)}
  if k=='ProblemCluster':
   incidents=self.sources('PART_OF',id)
   return {**base,'pattern_type':p['pattern_type'],'status':p['status'],'incident_ids':incidents,'related_asset_ids':sorted({a for i in incidents for a in self.targets('AFFECTS',i)}),'monitoring_status':p['status']}
  if k=='Investigation':
   bound=[self.repo.get_node(i) for i in self.targets('INVESTIGATES',id)];inc=[v for v in bound if v.kind=='Incident'];clusters=[v.id for v in bound if v.kind=='ProblemCluster'];plans=self.targets('PRODUCED_PLAN',id)
   context_assets=sorted({a for incident in inc for a in self.targets('AFFECTS',incident.id)}|{a for h in self.targets('PROPOSES',id) for a in self.targets('CONCERNS',h)})
   inspections=self.repo._read('MATCH (n:Inspection)-[:INSPECTS]->(a:InfrastructureAsset) WHERE a.id IN $assets RETURN DISTINCT n.id ORDER BY n.id LIMIT 101',{'assets':context_assets})
   if len(inspections)>100:raise PreconditionFailed('INSPECTION_READ_LIMIT')
   pending=[]
   for row in inspections:
    scope,_=EvidenceService(self.repo,clock=self.clock).inspection_source(Reader(self.repo,self.clock()),row[0])
    if scope['investigation_id']==id and self.repo.get_node(row[0]).properties['status'] not in {'COMPLETED','FAILED','CANCELLED'}:pending.append(row[0])
   return {**base,'status':p['status'],'incident_ids':[v.id for v in inc if v.properties['status']!='ENDED'],'historical_incident_ids':[v.id for v in inc if v.properties['status']=='ENDED'],'problem_cluster_id':clusters[0] if len(clusters)==1 else None,'active_hypothesis_ids':self.targets('PROPOSES',id),'pending_inspection_ids':pending,'current_plan_id':max(plans,key=lambda i:self.repo.get_node(i).properties['version']) if plans else None,'graph_revision':self.repo._read("MATCH (s:CivicSchemaMigration {id:'0001'}) RETURN s.repo_revision")[0][0]}
  if k=='Evidence':
   internal=p['evidence_type'] in {'B09_OPERATION','COMPLAINT_INTAKE','GROUPING_CORRECTION','B15_DELIVERY_AUDIT'}
   findings=self.targets('ESTABLISHES',id)
   reviewed=False;details={};ref=None
   try:ref=Reader(self.repo,self.clock()).evidence(id);reviewed=bool(ref.report and ref.report.review)
   except (ValueError,PreconditionFailed):
    if p['evidence_type']=='INSPECTION_REPORT':raise
   if ref and ref.report:
    report=ref.report
    details={'findings':[{'id':fid,'evidence_id':id,'observation':ob.model_dump(mode='json'),'verification_status':self.repo.get_node(fid,'Finding').properties['verification_status']} for fid,ob in zip(report.finding_ids,report.observations,strict=True)],'observation_source':{'inspection_id':report.inspection_id,'inspector_id':report.inspector_id,'department_id':report.department_id,'source_id':report.source_id,'record_id':report.record_id,'observed_at':report.observed_at,'recorded_at':report.recorded_at,'reviewed':reviewed,'reviewer_id':report.review.reviewer_id if report.review else None,'attribution':report.attribution.model_dump(mode='json') if report.attribution else None}}
   if p['evidence_type']=='SERVICE_EXECUTION_SOURCE':
    from app.services.service_evidence import parse_source,validate
    origin=parse_source(p);record=validate(self.repo,origin.report_evidence_id,self.clock())
    if not record or record.id!=id:raise PreconditionFailed('SERVICE_PROJECTION_SOURCE')
    reviewed=True;details={'service_record':record.model_dump(mode='json')}
   return {**base,'evidence_type':p['evidence_type'],'summary':'Internal provenance record; raw journal is not a public source' if internal else 'Attributed source evidence; findings are referenced separately','source_kind':p['source_kind'],'source_record_id':p.get('source_record_id'),'reliability':p['reliability'],'observed_at':p.get('observed_at'),'recorded_at':p['recorded_at'],'document_id':None,'finding_ids':findings,'reviewed':reviewed,**details,'limitations':[] if details else ['No validated typed inspection observations available; raw source journals withheld']}
  if k=='Inspection':
   view=EvidenceService(self.repo,clock=self.clock).inspection(id,self.clock());scope,_=EvidenceService(self.repo,clock=self.clock).inspection_source(Reader(self.repo,self.clock()),id)
   return {**base,'status':p['status'],'asset_ids':self.targets('INSPECTS',id),'department_id':scope['department_id'],'requested_at':view.requested_at,'scheduled_at':view.scheduled_at,'completed_at':view.completed_at,'assigned_inspector_id':p.get('inspector_id'),'evidence_ids':view.report_evidence_ids}
  if k=='Hypothesis':
   history=EvidenceService(self.repo,clock=self.clock).history(id,self.clock())
   last=history[-1] if history else None
   summaries=[{'id':a.id,'previous_assessment_id':a.previous_assessment_id,'assessment':a.assessment,'assessed_at':a.assessed_at,'supporting_evidence_ids':a.supporting_evidence_ids,'contradicting_evidence_ids':a.contradicting_evidence_ids,'missing_evidence':a.missing_evidence,'current':a.id==last.id} for a in history]
   return {**base,'statement':p['statement'],'cause_code':p['cause_code'],'status':p['status'],'current_assessment_id':last.id if last else None,'assessment_history':summaries,'supporting_evidence_ids':last.supporting_evidence_ids if last else [],'contradicting_evidence_ids':last.contradicting_evidence_ids if last else [],'missing_evidence':last.missing_evidence if last else ['No recorded assessment'],'suspected_asset_ids':self.targets('CONCERNS',id)}
  if k=='ResolutionPlan':
   s=self.ops.planning.store.get(id)
   if not s:raise PreconditionFailed('PLAN_READBACK')
   a=self.ops.store.get('plan',id)
   if a and a['native_hash']!=digest(p):raise PreconditionFailed('PLAN_LIFECYCLE_INTEGRITY')
   from .plan_bindings import task_bindings
   return {'task_bindings':task_bindings(self.ops,s),'plan_id':id,'investigation_id':s['draft']['investigation_id'],'version':s['receipt']['version'],'content_hash':s['receipt']['plan_hash'],'draft':s['draft'],'draft_receipt':s['receipt'],'status':p['status'],'expected_hash':n.content_hash,'approval_status':a['state'] if a else None,'execution_gates_verified':False,'simulated':True,'limitations':['Immutable draft receipt is not current execution authority','Approval does not prove all execution gates are satisfied','approval_status preserves the legacy plan lifecycle state; use ApprovalDTO.status for the approval decision']}
  if k=='Approval':
   a=self.ops.store.get('approval',id)
   if not a:raise PreconditionFailed('APPROVAL_UNAVAILABLE')
   self.ops.approval(id,a['binding']);b=a['binding']
   return {**base,'plan_id':b['plan_id'],'plan_version':b['plan_version'],'plan_hash':b['plan_hash'],'assignments':b['assignments'],'status':p['status'],'approved_by':a.get('decided_by') if p['status']=='APPROVED' else None,'requested_at':p['requested_at'],'scope_hash':digest(b)}
  if k=='WorkOrder':
   v=self.ops.read_work_order(id,token=token)
   outcomes=[self.ops.store.get('outcome',oid) for oid in self.targets('RESULTED_IN',id)]
   if any(o is None or o['work_order_id']!=id for o in outcomes):raise PreconditionFailed('OUTCOME_READ_INTEGRITY')
   latest=max(outcomes,key=lambda o:(timestamp(o['evaluated_at']),o['id'])) if outcomes else None
   return {**base,'resolution_verified':bool(latest and latest['assessment_status']=='RESOLUTION_VERIFIED'),'latest_assessment_status':latest['assessment_status'] if latest else None,'status':p['status'],'task_id':v['assignment']['task_id'],'plan_id':v['binding']['plan_id'],'department_id':v['assignment']['department_id'],'assignee_id':v['assignment']['assignee_id'],'authorized_by':v['authorized_by'],'status_event_ids':self.targets('HAS_EVENT',id)}
  if k=='Department':return {**base,**{f:p[f] for f in ['name','department_type']}}
  raise ValueError('READ_PROJECTION_UNAVAILABLE')
 def outcome(self,v):
  return {'id':v['id'],'work_order_id':v['work_order_id'],'assessment_status':v['assessment_status'],'result':v['result'],'evidence_ids':[ref['id'] for ref in v.get('evidence_references',[])],'evaluated_at':v.get('evaluated_at',v.get('recorded_at')),'case_closed':v.get('case_closed',False),'policy_version':v.get('policy_version'),'simulated':True}
 async def document(self,id,actor,token):
  if not self.memory:raise PreconditionFailed('MEMORY_DEPENDENCY_REQUIRED')
  item=self.memory.store.get(id)
  if not item:
   if actor.role=='DEPARTMENT_LEAD':raise Denied('DOCUMENT_SCOPE_DENIED')
   raise NotFound('DOCUMENT_UNAVAILABLE')
  source=item[0]
  if actor.role=='DEPARTMENT_LEAD' and source.owner_department_id!=actor.department_id:raise Denied('DOCUMENT_SCOPE_DENIED')
  found=await self.memory.retrieve(as_of=self.clock(),document_id=source.document_id,version=source.version)
  return {'id':source.id,'title':source.title,'source_kind':source.source_kind,'version':source.version,'sha256':source.sha256,'owner_department_id':source.owner_department_id,'citations':found['citations'],'gaps':found['gaps']}
 async def procedures(self,actor,token,limit,cursor):
  if not self.memory:raise PreconditionFailed('MEMORY_DEPENDENCY_REQUIRED')
  rows=[]
  for source,_,_ in self.memory.store.all():
   if actor.role=='DEPARTMENT_LEAD' and source.owner_department_id!=actor.department_id:continue
   if not source.active(self.clock()):continue
   doc=await self.document(source.id,actor,token)
   rows.append({**doc,'procedure_id':source.id.replace('ORG:','ORGPROC:',1),'effective_from':source.effective_from})
  return self.page(rows,limit,cursor)
 def plans(self,id,actor,token,limit,cursor):
  self.node(id,'Investigation',actor,token)
  rows=[]
  for plan in self.targets('PRODUCED_PLAN',id):
   n=self.repo.get_node(plan,'ResolutionPlan')
   if Reader(self.repo,self.clock()).visible(n.properties) and self.allowed(n,actor,token):rows.append(self.project(n,actor,token))
  return self.page(rows,limit,cursor)
 def outcomes(self,id,actor,token,limit,cursor):
  self.node(id,'ProblemCluster',actor,token);rows=[]
  incidents=set(self.sources('PART_OF',id))
  outcome_rows=self.ops.store.repo._read("MATCH (s:CivicOperationState {kind:'outcome'}) RETURN s.id ORDER BY s.id LIMIT 501")
  if len(outcome_rows)>500:raise PreconditionFailed('OUTCOME_SCAN_LIMIT')
  for outcome in outcome_rows:
   v=self.ops.store.get('outcome',outcome[0].removeprefix('outcome:'))
   if len(rows)>500:raise PreconditionFailed('OUTCOME_SCAN_LIMIT')
   # Scope through authenticated work-order projection before revealing outcomes.
   w=self.repo.get_node(v['work_order_id'],'WorkOrder')
   if not self.allowed(w,actor,token):continue
   order=self.ops.store.get('order',w.id);inv=self.ops.planning.store.get(order['binding']['plan_id'])['draft']['investigation_id']
   if incidents&set(self.targets('INVESTIGATES',inv)):rows.append(self.outcome(v))
  return self.page(rows,limit,cursor)
 def monitoring(self,actor,token,limit,cursor):
  rows=[]
  for id in self.ids('ProblemCluster'):
   n=self.repo.get_node(id,'ProblemCluster')
   if not self.allowed(n,actor,token):continue
   out=self.outcomes(id,actor,token,50,None)['items']
   rows.append({'problem_cluster_id':id,'status':n.properties['status'],'verification_policy':'B14-2; actual dated evidence/opportunity required','remaining_checks':[] if n.properties['status']=='CONTROLLED' and any(v['case_closed'] for v in out) else ['Independent observation opportunity and verification remain required'],'outcome_evidence_ids':sorted({i for v in out for i in v['evidence_ids']})})
  return self.page(rows,limit,cursor)
 def completed_case_context(self,id,actor,token):
  incident=self.node(id,'Incident',actor,token)
  if incident.properties['status']!='ENDED':return None
  # Graph identity chain supplies the episode scope; immutable operation storage
  # supplies attributable evidence. No guessed similarities or generated lesson.
  linked=self.repo._read('MATCH (i:Investigation)-[:INVESTIGATES]->(:Incident {id:$id}) MATCH (i)-[:PRODUCED_PLAN]->(p:ResolutionPlan)-[:HAS_TASK]->(:ActionTask)<-[:IMPLEMENTS]-(w:WorkOrder)-[:RESULTED_IN]->(o:InterventionOutcome) RETURN DISTINCT i.id,p.id,w.id,o.id ORDER BY o.id LIMIT 101',{'id':id})
  if len(linked)>100:raise PreconditionFailed('CASE_MEMORY_OUTCOME_LIMIT')
  evidence=set();outcomes=[];invs=set()
  for inv,pid,wid,oid in linked:
   if not all(self.allowed(self.repo.get_node(target),actor,token) for target in [inv,wid,oid]):continue
   value=self.ops.store.get('outcome',oid)
   if not value or (value['id'],value['work_order_id'],value['plan_id'])!=(oid,wid,pid):raise PreconditionFailed('CASE_MEMORY_OUTCOME_BINDING')
   outcomes.append(oid);invs.add(inv)
   for ref in value['evidence_references']:
    node=self.node(ref['id'],'Evidence',actor,token)
    if node.content_hash!=ref['content_hash']:raise PreconditionFailed('CASE_MEMORY_EVIDENCE_CHANGED')
    evidence.add(node.id)
  if not outcomes:return None
  if len(evidence)>100:raise PreconditionFailed('CASE_MEMORY_EVIDENCE_LIMIT')
  return {'id':id,'source_investigation_id':next(iter(invs)) if len(invs)==1 else None,'outcome_ids':sorted(set(outcomes)),'evidence_ids':sorted(evidence),'gaps':['Recorded completed episode, not an automatically generalized lesson; synthetic outcome policy and original assessment gaps remain applicable'],'truncated':False}
 def case_memory(self,id,actor,token,limit,cursor):
  self.node(id,'Incident',actor,token)
  from app.graph.analysis.engine import GraphAnalysis
  from app.graph.analysis.models import CaseRequest
  result=GraphAnalysis(self.repo).cases(CaseRequest(seed_incident_id=id,as_of=self.clock(),limit=40,max_hops=4,include_candidates=False))
  rows=[];nodes={n.id:n for n in result.nodes}
  for row in result.rows:
   n=self.repo.get_node(row.id,'Incident')
   if not self.allowed(n,actor,token):continue
   outcome_ids=[i for i in row.related_ids if i in nodes and nodes[i].kind=='InterventionOutcome']
   if actor.role=='DEPARTMENT_LEAD':
    visible=[]
    for oid in outcome_ids:
     orders=self.sources('RESULTED_IN',oid)
     if orders and all(self.allowed(self.repo.get_node(w,'WorkOrder'),actor,token) for w in orders):visible.append(oid)
    outcome_ids=visible
   invs=[i for i in self.sources('INVESTIGATES',row.id) if self.allowed(self.repo.get_node(i,'Investigation'),actor,token)]
   evidence_ids=sorted({i for path in result.paths if path.id in row.path_ids for i in path.evidence_ids})
   if actor.role=='DEPARTMENT_LEAD':evidence_ids=[i for i in evidence_ids if self.allowed(self.repo.get_node(i,'Evidence'),actor,token)]
   rows.append({'id':row.id,'source_investigation_id':invs[0] if len(invs)==1 else None,'outcome_ids':outcome_ids,'evidence_ids':evidence_ids,'gaps':list(dict.fromkeys([*row.gaps,*result.gaps])),'truncated':result.truncated})
  own=self.completed_case_context(id,actor,token)
  if own and not any(row['id']==id for row in rows):rows.append(own)
  page=self.page(rows,limit,cursor);page.update(limitations=list(result.gaps)+list(result.reservations),truncated=result.truncated or result.search_limited)
  return page
