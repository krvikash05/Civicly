"""Authoritative public draft-to-native task mapping; never execution authority."""
from app.graph.repository import PreconditionFailed
from app.services.operations.auth import OPERATORS,Denied


def task_bindings(ops,saved):
 tasks=saved['draft']['tasks'];ids=saved['task_ids'];plan=saved['receipt']['id']
 def require(condition):
  if not condition:raise PreconditionFailed('PLAN_TASK_BINDING_INTEGRITY')
 require(set(ids)=={t['id'] for t in tasks} and len(set(ids.values()))==len(tasks))
 require(sorted(ops.projection('HAS_TASK',plan))==sorted(ids.values()))
 rows=[]
 for t in tasks:
  node=ops.repo.get_node(ids[t['id']],'ActionTask')
  dependencies=sorted(ids[id] for id in t['depends_on'])
  require(node.properties['action_type']==t['action_type'])
  require(ops.projection('ASSIGNED_TO',node.id)==[t['department_id']])
  require(sorted(ops.projection('TARGETS',node.id))==sorted(t['target_ids']))
  require(sorted(ops.projection('DEPENDS_ON',node.id))==dependencies)
  eligible=[]
  for id,(role,department) in OPERATORS.items():
   if role!='DEPARTMENT_LEAD' or department!=t['department_id']:continue
   try:actor=ops.auth.operator(id)
   except Denied:continue
   if actor.role==role and actor.department_id==department:eligible.append(id)
  rows.append({'local_task_id':t['id'],'task_id':node.id,'action_type':t['action_type'],
   'target_ids':sorted(t['target_ids']),'department_id':t['department_id'],
   'depends_on_task_ids':dependencies,'status':node.properties['status'],
   'expected_hash':node.content_hash,'eligible_assignee_ids':sorted(eligible)})
 return rows
