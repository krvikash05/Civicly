"""Additive0004 companion; one fenced statement commits complete draft graph."""
import json,hashlib
from pathlib import Path
from app.graph.migration import MigrationRunner,MigrationError
from app.graph.schema import utc_now
from app.graph.models import digest
from .models import PlanDraft,PlanReceipt
PLAN=Path(__file__).resolve().parents[2]/'graph/migrations/0004_plan_drafts.json'
class PlanMigration:
 def __init__(self,client,name):
  self.base=MigrationRunner(client,name);self.graph=self.base.graph;self.client=client
  self.plan=json.loads(PLAN.read_text());self.checksum=hashlib.sha256(PLAN.read_bytes()).hexdigest()
  if self.base.checksum!=self.plan['requires_0001_sha256']:raise MigrationError('0001 mismatch')
 def status(self):
  rows=self.graph.ro_query('MATCH (m:CivicPlanMigration {id:$id}) RETURN m.checksum,m.state LIMIT 2',params={'id':'0004'}).result_set
  if len(rows)>1 or rows and (rows[0][0]!=self.checksum or rows[0][1] not in {'APPLYING','FAILED','READY'}):raise MigrationError('0004 checksum mismatch')
  ready=bool(rows and rows[0][1]=='READY')
  if ready:
   for key in ['indexes','constraints']:
    for spec in self.plan[key]:self.base._wait(key,spec,.1)
  return {'id':'0004','ready':ready,'checksum':self.checksum}
 def apply(self,retry_failed=False):
  if not self.base.status()['ready']:raise MigrationError('0001 not READY')
  lock=self.client.connection.lock('civicly:plan-migration:'+self.graph.name,timeout=30,blocking_timeout=1)
  if not lock.acquire():raise MigrationError('Migration busy')
  def state(value):self.graph.query('MERGE (m:CivicPlanMigration {id:$id}) SET m.checksum=$sha,m.state=$state,m.updated_at=$at',params={'id':'0004','sha':self.checksum,'state':value,'at':utc_now()})
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
  if not PlanMigration(repo.client,repo.graph.name).status()['ready']:raise MigrationError('Plan storage not READY; apply0004 explicitly')
 def rows(self,inv):
  rows=self.repo._read('MATCH (d:CivicPlanDraft {investigation_id:$id}) RETURN d.id,d.version,d.request_id LIMIT 101',{'id':inv})
  if len(rows)>100:raise ValueError('PLAN_HISTORY_LIMIT')
  return rows
 def get(self,id):
  rows=self.repo._read('MATCH (p:ResolutionPlan {id:$id}),(d:CivicPlanDraft {id:$id}) RETURN properties(p),d.payload_json,d.payload_sha256 LIMIT 2',{'id':id})
  if not rows:return None
  if len(rows)!=1:raise ValueError('PLAN_IDENTITY')
  props,raw,sha=rows[0];self.repo.registry.validate_node('ResolutionPlan',props);payload=json.loads(raw)
  draft=PlanDraft.model_validate(payload['draft']);receipt=PlanReceipt.model_validate(payload['receipt'])
  if digest(payload)!=sha or draft.content_hash!=receipt.plan_hash or props['plan_hash']!=receipt.plan_hash or props['version']!=receipt.version :raise ValueError('PLAN_INTEGRITY')
  lifecycle=self.repo._read('MATCH (s:CivicOperationState {id:$id,kind:$kind}) RETURN s.id LIMIT 2',{'id':'plan:'+id,'kind':'plan'})
  if props['status']!='DRAFT' or lifecycle:
   from app.services.operations.storage import verify_plan_lifecycle
   verify_plan_lifecycle(self.repo,props,receipt)
  return payload
 def commit(self,session,draft,receipt,request_id,proof,at):
  common=lambda id:{'id':id,'municipality_id':'demo-city','created_at':at}
  nodes={receipt.id:('ResolutionPlan',{**common(receipt.id),'updated_at':at,'schema_version':3,'version':receipt.version,'status':'DRAFT','plan_hash':receipt.plan_hash,'graph_revision':session.revision+1})}
  task_ids={t.id:'TASK-B12-'+digest([receipt.id,t.id])[:32] for t in draft.tasks}
  for task in draft.tasks:nodes[task_ids[task.id]]=('ActionTask',{**common(task_ids[task.id]),'updated_at':at,'schema_version':3,'status':'PROPOSED','action_type':task.action_type,'priority':task.priority})
  edge_specs=[('PRODUCED_PLAN',draft.investigation_id,receipt.id)]
  for task in draft.tasks:
   id=task_ids[task.id];edge_specs += [('HAS_TASK',receipt.id,id),('ASSIGNED_TO',id,task.department_id)]
   edge_specs += [('TARGETS',id,target) for target in task.target_ids]
   edge_specs += [('DEPENDS_ON',id,task_ids[dependency]) for dependency in task.depends_on]
  external={id for _,a,b in edge_specs for id in [a,b] if id not in nodes}
  aliases={id:'n'+str(i) for i,id in enumerate(sorted(set(nodes)|external))};params={};matches=[];creates=[]
  for id in sorted(external):
   alias=aliases[id];record=self.repo.get_node(id);nodes[id]=(record.kind,record.properties)
   matches.append(f'({alias}:CivicEntity {{id:${alias}_id,municipality_id:$scope}})');params[alias+'_id']=id
  for id in sorted(set(nodes)-external):
   kind,props=nodes[id];self.repo.registry.validate_node(kind,props)
   if self.repo._node_optional(id) or self.repo._edge_optional(id):raise ValueError('PLAN_ID_COLLISION')
   alias=aliases[id];creates.append(f'CREATE ({alias}:'+':'.join(self.repo.registry.labels(kind))+f') SET {alias}=${alias}_props ');params[alias+'_props']=props
  for i,(kind,source,target) in enumerate(edge_specs):
   edge=common('REL-B12-'+digest([receipt.id,kind,source,target])[:32]);sk,sp=nodes[source];tk,tp=nodes[target]
   self.repo.registry.validate_edge(kind,sk,sp,tk,tp,edge)
   # New, version-owned task IDs and validated DAG cannot collide with old DAGs.
   creates.append(f'CREATE ({aliases[source]})-[e{i}:{kind}]->({aliases[target]}) SET e{i}=$edge{i} ');params['edge'+str(i)]=edge
  payload={'draft':draft.normalized(),'receipt':receipt.model_dump(mode='json'),'request_id':request_id,'proof':proof,'task_ids':task_ids}
  raw=json.dumps(payload,sort_keys=True,separators=(',',':'))
  if len(raw.encode())>90000:raise ValueError('PLAN_PAYLOAD_LIMIT')
  detail={'id':receipt.id,'investigation_id':draft.investigation_id,'version':draft.version,'request_id':request_id,'state':'DRAFT','payload_json':raw,'payload_sha256':digest(payload)}
  body='MATCH '+','.join(matches)+' '+''.join(creates)+'CREATE (detail:CivicPlanDraft) SET detail=$detail '
  self.repo._commit(session,'node',receipt.id,'',body,{**params,'scope':'demo-city','detail':detail},aliases[receipt.id])
  return payload
