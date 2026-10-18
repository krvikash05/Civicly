"""Fixed B13 batch compiler and hashed companion reads; existing writer fence."""
import json
from app.graph.models import digest
from app.graph.schema import timestamp
from app.graph.repository import Conflict,PreconditionFailed
from .models import OpsRecovery
NODES={'PickupExecution','Approval','WorkOrder','DomainEvent','StatusEvent','InterventionOutcome','Evidence','Finding','Inspection','HypothesisAssessment','Complaint','Incident','ProblemCluster'}
UPDATES={'DomainEvent','ResolutionPlan','ActionTask','Approval','WorkOrder','Inspection','Hypothesis','Incident','Investigation','ProblemCluster'}
EDGES={'PICKUP_FOR','MAINTAINED_BY','INVESTIGATES','IMPLEMENTS','AUTHORIZED_BY','HAS_EVENT','EMITTED_EVENT','RESULTED_IN','INSPECTS','PRODUCED','ESTABLISHES','HAS_ASSESSMENT','SUPPORTED_BY','CONTRADICTED_BY','REPORTS','OCCURRED_AT','AFFECTS','PART_OF'}
class Storage:
 def __init__(self,repo):self.repo=repo
 def get(self,kind,id):
  rows=self.repo._read('MATCH (s:CivicOperationState {id:$id,kind:$kind}) RETURN s.payload_json,s.payload_sha256 LIMIT 2',{'id':kind+':'+id,'kind':kind})
  if not rows:return None
  if len(rows)!=1:raise PreconditionFailed('OPERATIONS_IDENTITY')
  v=json.loads(rows[0][0])
  if digest(v)!=rows[0][1]:raise PreconditionFailed('OPERATIONS_INTEGRITY')
  return v
 def commit(self,session,subject,nodes,updates,edges,states):
  if len(nodes)>45 or len(updates)>30 or len(edges)>60 or len(states)>10:raise PreconditionFailed('OPERATIONS_BATCH_LIMIT')
  records={};fresh={id for kind,props in nodes for id in [props['id']]}
  for kind,props in nodes:
   if kind not in NODES or props['id'] in records or self.repo._node_optional(props['id']) or self.repo._edge_optional(props['id']):raise Conflict('OPERATIONS_COLLISION')
   self.repo.registry.validate_node(kind,props);records[props['id']]=(kind,props)
  for old,props in updates:
   if old.kind not in UPDATES or props['id']!=old.id:raise PreconditionFailed('OPERATIONS_UPDATE_SCOPE')
   allowed={'updated_at','delivery_status','processed_at'} if old.kind=='DomainEvent' else {'status','updated_at','graph_revision','decided_at','decided_by'}
   allowed |= {'scheduled_at','completed_at'} if old.kind=='Inspection' else {'ended_at'} if old.kind=='Incident' else {'pattern_type','first_seen_at'} if old.kind=='ProblemCluster' else set()
   if any(props.get(k)!=v for k,v in old.properties.items() if k not in allowed) or set(props)-set(old.properties)-allowed:raise PreconditionFailed('OPERATIONS_IMMUTABLE_FIELDS')
   if timestamp(props['updated_at'])<timestamp(old.properties['updated_at']):raise PreconditionFailed('OPERATIONS_TIME_ROLLBACK')
   self.repo.registry.validate_node(old.kind,props);records[old.id]=(old.kind,props)
  for kind,a,b,props in edges:
   if kind not in EDGES:raise PreconditionFailed('OPERATIONS_EDGE_SCOPE')
   for id in [a,b]:
    if id not in records:
     n=self.repo.get_node(id);records[id]=(n.kind,n.properties)
   source=self.repo.decode_node(self.repo.registry.labels(records[a][0]),records[a][1]);target=self.repo.decode_node(self.repo.registry.labels(records[b][0]),records[b][1])
   self.repo.registry.validate_edge(kind,source.kind,source.properties,target.kind,target.properties,props)
   policy_props=props
   evidence=props.get('source_evidence_id')
   planned=None
   if evidence in fresh and kind=='MAINTAINED_BY':
    ek,ep=records[evidence]
    from app.services.responsibility.service import validate_review_evidence
    if ek!='Evidence' or props.get('association_status')!='VERIFIED':raise PreconditionFailed('PLANNED_RESPONSIBILITY_SOURCE')
    review,assertion=validate_review_evidence(self.repo,ep)
    if (a,b,props.get('valid_from'),props.get('valid_to'))!=(assertion.command.asset_id,assertion.command.department_id,assertion.command.valid_from,assertion.command.valid_to):raise PreconditionFailed('PLANNED_RESPONSIBILITY_SCOPE')
    planned=self.repo.decode_node(self.repo.registry.labels('Evidence'),ep)
   elif evidence in fresh and kind=='PICKUP_FOR':
    from app.services.service_evidence import parse_source
    ek,ep=records[evidence];record=parse_source(ep)
    if ek!='Evidence' or (a,b)!=(record.pickup_id,record.target_id) or records[a][0]!='PickupExecution' or records[a][1].get('route_id')!=record.route_id:raise PreconditionFailed('PLANNED_SERVICE_SOURCE_SCOPE')
    self.repo._check_evidence(props,planned=self.repo.decode_node(self.repo.registry.labels('Evidence'),ep))
    policy_props={k:v for k,v in props.items() if k!='source_evidence_id'}
   elif evidence in fresh:
    # B09/B08 command journal is created atomically with its links. Validate that
    # narrow planned source rather than weakening B03's persisted-source checks.
    ek,ep=records[evidence]
    if ek!='Evidence' or ep['evidence_type'] not in {'B09_OPERATION','COMPLAINT_INTAKE'} or ep['reliability']!='UNVERIFIED' or props.get('association_status')=='VERIFIED':raise PreconditionFailed('PLANNED_OPERATION_EVIDENCE_SCOPE')
    if timestamp(ep['recorded_at'])>timestamp(props['created_at']):raise PreconditionFailed('PLANNED_OPERATION_EVIDENCE_TIME')
    policy_props={k:v for k,v in props.items() if k!='source_evidence_id'}
   self.repo._relationship_policies(kind,source,target,policy_props,planned_evidence=planned)
   if self.repo._edge_optional(props['id']):raise Conflict('OPERATIONS_EDGE_COLLISION')
  from app.graph.repository import interval,intersection
  for i,(kind,a,b,props) in enumerate(edges):
   for other,c,d,previous in edges[:i]:
    if kind==other and a==c and intersection(interval(props),interval(previous)) is not None and (b==d or kind in self.repo.policy['singleton_outgoing']):raise Conflict('OPERATIONS_BATCH_CARDINALITY')
  if subject not in records:
   n=self.repo.get_node(subject);records[subject]=(n.kind,n.properties)
  aliases={id:'n'+str(i) for i,id in enumerate(sorted(records))};params={'scope':'demo-city'};parts=[]
  for id in sorted(set(records)-fresh):
   alias=aliases[id];parts.append(f'MATCH ({alias}:CivicEntity {{id:${alias}_id,municipality_id:$scope}}) ');params[alias+'_id']=id
  for kind,props in nodes:
   alias=aliases[props['id']];parts.append(f'CREATE ({alias}:'+':'.join(self.repo.registry.labels(kind))+f') SET {alias}=${alias}_props ');params[alias+'_props']=props
  for i,(old,props) in enumerate(updates):parts.append(f'SET {aliases[old.id]}=$update{i} ');params['update'+str(i)]=props
  for i,(kind,a,b,props) in enumerate(edges):parts.append(f'CREATE ({aliases[a]})-[e{i}:{kind}]->({aliases[b]}) SET e{i}=$edge{i} ');params['edge'+str(i)]=props
  for i,(kind,id,value) in enumerate(states):
   raw=json.dumps(value,sort_keys=True,separators=(',',':'))
   if len(raw.encode())>150000:raise PreconditionFailed('OPERATIONS_PAYLOAD_LIMIT')
   # All keys generated internally and protected by0005 unique constraint.
   parts.append(f'MERGE (s{i}:CivicOperationState {{id:$stateid{i}}}) SET s{i}.kind=$kind{i},s{i}.payload_json=$raw{i},s{i}.payload_sha256=$sha{i} ')
   params.update({f'stateid{i}':kind+':'+id,f'kind{i}':kind,f'raw{i}':raw,f'sha{i}':digest(value)})
  before=self.repo._node_optional(subject)
  self.repo._commit(session,'node',subject,before.content_hash if before else '', ''.join(parts),params,aliases[subject])

def verify_plan_lifecycle(repo,props,receipt):
 """Historical B12 bytes stay immutable; independently attest current native state."""
 store=Storage(repo);v=store.get('plan',props['id'])
 if not v or v['state']!=props['status'] or v['native_hash']!=digest(props):raise PreconditionFailed('PLAN_LIFECYCLE_INTEGRITY')
 binding=v['binding']
 if binding['plan_id']!=props['id'] or binding['plan_version']!=receipt.version or binding['plan_hash']!=receipt.plan_hash:raise PreconditionFailed('PLAN_LIFECYCLE_BINDING')
 op=store.get('operation',v['last_operation'])
 if not op or op['native_hashes'].get(props['id'])!=digest(props):raise PreconditionFailed('PLAN_LIFECYCLE_AUDIT')
 if props['status'] not in {'PENDING_APPROVAL','APPROVED','REJECTED','SUPERSEDED','IN_EXECUTION','MONITORING','COMPLETED'}:raise PreconditionFailed('PLAN_LIFECYCLE_UNSUPPORTED')
