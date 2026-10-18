"""Static bounded feedback. Never echo exception strings, ctx messages or inputs."""
import re
from typing import Literal,Annotated
from pydantic import Field,ValidationError
from app.services.evidence.models import Model
from app.graph.migration import MigrationError
from app.graph.repository import OutcomeUnknown
from .service import PlanningBlocked
class Feedback(Model):
 code:Literal['PLAN_DAG_INVALID','PLAN_SCHEMA_INVALID','PLAN_ACTION_UNSUPPORTED','PLAN_PREREQUISITE_INVALID','PLAN_EVIDENCE_INSUFFICIENT','PLAN_OWNERSHIP_UNAVAILABLE','PLAN_SOURCE_UNAVAILABLE','PLAN_DEPENDENCY_UNAVAILABLE','PLAN_OPERATOR_RECOVERY','PLAN_REFERENCE_INVALID']
 category:Literal['DAG','SCHEMA','ACTION','PREREQUISITE','EVIDENCE','OWNERSHIP','SOURCE','DEPENDENCY','RECOVERY','REFERENCE']
 resolution:Literal['DRAFT_CLARIFICATION','MISSING_EVIDENCE_OR_CAPABILITY','OPERATOR_RECOVERY']
 task_ids:list[Annotated[str,Field(max_length=64,pattern=r'^[A-Za-z][A-Za-z0-9_.-]*$')]]=Field(default_factory=list,max_length=8)
 field_paths:list[Annotated[str,Field(max_length=160)]]=Field(default_factory=list,max_length=8)
 explanation:str=Field(max_length=240)
 draft_committed:Literal['NO','UNKNOWN']='NO'

def feedback(error):
 code,category,resolution,message='PLAN_OPERATOR_RECOVERY','RECOVERY','OPERATOR_RECOVERY','Stop and reconcile storage, ownership and the last durable checkpoint before retrying.'
 paths=[];tasks=[];committed='UNKNOWN'
 if isinstance(error,ValidationError):
  code,category,resolution,message='PLAN_SCHEMA_INVALID','SCHEMA','DRAFT_CLARIFICATION','Correct the indicated draft fields without changing evidence or execution authority.';committed='NO'
  # Known schema property names only; extra-property names may themselves contain secrets.
  allowed={'tasks','id','action_type','target_ids','department_id','depends_on','assessment_ids','evidence_ids','procedure_citation','remediation','conditions','kind','status','mode','depends_on_task_id','basis','monitoring','version','previous_plan_id','expected_outcome','verification_criteria','prerequisites','risks'}
  for e in error.errors(include_url=False,include_context=True,include_input=False)[:8]:
   loc=e['loc'];safe=[str(v) for v in loc if type(v) is int or v in allowed]
   if safe:paths.append('.'.join(safe)[:160])
   task=(e.get('ctx') or {}).get('task_id')
   if isinstance(task,str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,63}',task):tasks.append(task)
   if e['type']=='plan_dag':code,category,message='PLAN_DAG_INVALID','DAG','Correct cyclic or unknown task dependencies; retain inspection and evidence gates.'
   elif e['type']=='plan_prerequisite':code,category,message='PLAN_PREREQUISITE_INVALID','PREREQUISITE','Represent causal inspection and safety gates explicitly; text cannot satisfy a missing gate.'
   elif loc and loc[-1]=='action_type':code,category,message='PLAN_ACTION_UNSUPPORTED','ACTION','Select an admitted action or request an evidence-grounded inspection.'
 elif isinstance(error,PlanningBlocked) and error.code!='PLAN_READBACK':
  committed='NO';resolution='MISSING_EVIDENCE_OR_CAPABILITY'
  c=error.code
  if c.startswith(('OWNERSHIP','ACCOUNTABLE_DEPARTMENT')):code,category,message='PLAN_OWNERSHIP_UNAVAILABLE','OWNERSHIP','Resolve verified accountable ownership before resubmitting this task.'
  elif c.startswith('PROCEDURE'):code,category,message='PLAN_SOURCE_UNAVAILABLE','SOURCE','Retrieve a current applicable non-revoked source version through the authorized memory capability.'
  elif c.startswith('PREREQUISITE'):code,category,message='PLAN_PREREQUISITE_INVALID','PREREQUISITE','Supply valid typed gate evidence or an explicit inspection dependency.';resolution='DRAFT_CLARIFICATION'
  elif c in {'REMEDIAL_EVIDENCE_INSUFFICIENT','REMEDIAL_EVIDENCE_CHANGED'}:code,category,message='PLAN_EVIDENCE_INSUFFICIENT','EVIDENCE','Remediation lacks reviewed causal support; retain inspection to resolve the evidence gap.'
  elif c=='ACTION_TARGET_OR_DEPARTMENT':code,category,message='PLAN_ACTION_UNSUPPORTED','ACTION','Use an admitted issue, target subtype and accountable department combination.';resolution='DRAFT_CLARIFICATION'
  elif c=='EVIDENCE_OUTSIDE_ASSESSMENTS':
   code,category,message='PLAN_REFERENCE_INVALID','REFERENCE','Draft evidence_ids must be supporting or contradicting evidence of the latest basis assessments; graph-context sources alone are not plan evidence.';resolution='DRAFT_CLARIFICATION';paths=['evidence_ids']
  else:code,category,message='PLAN_REFERENCE_INVALID','REFERENCE','Revalidate current investigation, assessment, version and evidence references.';resolution='DRAFT_CLARIFICATION'
  if error.task_id and re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,63}',error.task_id):tasks=[error.task_id]
 elif isinstance(error,MigrationError):code,category,message='PLAN_DEPENDENCY_UNAVAILABLE','DEPENDENCY','Operator must establish ready compatible plan storage before retrying.';committed='NO'
 return Feedback(code=code,category=category,resolution=resolution,task_ids=list(dict.fromkeys(tasks))[:8],field_paths=list(dict.fromkeys(paths))[:8],explanation=message,draft_committed=committed)
