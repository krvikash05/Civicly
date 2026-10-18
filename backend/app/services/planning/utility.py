"""Closed utility DAG rules; future evidence cannot be asserted by a draft."""
DYNAMIC = {'ISOLATION_PROOF','UTILITY_VERIFICATION'}

def underlies(reader,pipe):
 # Reuse verified-only bounded B05 traversal rather than broaden B09 read families.
 from app.services.evidence.models import Topology
 result=reader.topology(Topology(source_id=pipe,target_id=pipe,operation='dependencies',max_hops=6))
 if result.truncated:
  from app.graph.repository import PreconditionFailed
  raise PreconditionFailed('UTILITY_TOPOLOGY_TRUNCATED')
 edges={e.id:e for e in result.edges}
 return {p.node_ids[-1] for p in result.paths if len(p.edge_ids)==1 and edges[p.edge_ids[0]].kind=='UNDERLIES' and p.directions==('OUTGOING',)}

def validate_dependencies(task,draft,reader,reject):
 conditions={c.kind:c for c in task.remediation.conditions}
 dynamic=set(conditions)&DYNAMIC
 tasks={t.id:t for t in draft.tasks}
 expected=set();linked=[]
 if task.action_type=='UTILITY_LEAK_REPAIR':expected={'ISOLATION_PROOF'}
 if task.action_type=='SUBGRADE_REPAIR':
  # Explicit reviewed topology determines whether this road shares the pipe.
  linked=[t for t in draft.tasks if t.action_type=='UTILITY_LEAK_REPAIR' and any(set(task.target_ids)&underlies(reader,pipe) for pipe in t.target_ids)]
  if len(linked)>1:reject('UTILITY_MULTIPLE_REPAIR_PREDECESSORS')
  if linked:expected={'UTILITY_VERIFICATION'}
 if dynamic!=expected:reject('UTILITY_DEPENDENCY_REQUIRED')
 for kind in dynamic:
  c=conditions[kind];dep=tasks.get(c.depends_on_task_id)
  action='UTILITY_ISOLATION' if kind=='ISOLATION_PROOF' else 'UTILITY_LEAK_REPAIR'
  if c.status!='UNMET' or c.evidence_ids or not dep or dep.id not in task.depends_on or dep.action_type!=action:reject('UTILITY_DEPENDENCY_BINDING')
  if kind=='ISOLATION_PROOF' and set(dep.target_ids)!=set(task.target_ids):reject('UTILITY_DEPENDENCY_TARGET')
  if kind=='UTILITY_VERIFICATION' and dep.id!=linked[0].id:reject('UTILITY_DEPENDENCY_BINDING')
  if kind=='UTILITY_VERIFICATION' and not all(any(target in underlies(reader,pipe) for pipe in dep.target_ids) for target in task.target_ids):reject('UTILITY_DEPENDENCY_TARGET')
 if task.action_type in {'UTILITY_ISOLATION','UTILITY_LEAK_REPAIR'} or dynamic:
  if any(conditions[k].status!='MET' for k in ['CAUSAL_INSPECTION','SAFETY_REVIEW']):reject('UTILITY_CURRENT_EVIDENCE_REQUIRED')
  if set(task.depends_on)!={conditions[k].depends_on_task_id for k in dynamic}:reject('UTILITY_DEPENDENCY_SCOPE')
