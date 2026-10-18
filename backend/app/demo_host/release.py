"""Presenter-controlled synthetic inspection results; never an agent tool."""
from pathlib import Path
from app.graph.models import digest
from app.graph.schema import utc_now
from app.services.evidence.service import EvidenceService
from app.services.evidence.reader import Reader
from cli.private import read_json,write_private
from .runtime import HostBlocked


def release(config,repo,case_id,inspection_id):
 case=next((c for c in config.cases if c.investigation_id==case_id),None)
 if case is None:raise HostBlocked('CASE_NOT_HOST_AUTHORIZED')
 from app.services.operations.auth import Auth
 auth=Auth(config.auth_store)
 passwords=read_json(Path(config.auth_store).parent/'presenter-credentials.json',private=True)
 ev=EvidenceService(repo,clock=utc_now)
 scope,assets=ev.inspection_source(Reader(repo,utc_now()),inspection_id)
 if scope['investigation_id']!=case_id:raise HostBlocked('INSPECTION_CASE_MISMATCH')
 who={'DEPT-DRAIN':'OP-DRAIN-LEAD','DEPT-WATER':'OP-WATER-LEAD','DEPT-ROAD':'OP-ROAD-LEAD','DEPT-SAN':'OP-WASTE-LEAD'}.get(scope['department_id'])
 if not who:raise HostBlocked('INSPECTION_DEPARTMENT_UNSUPPORTED')
 marker=Path(config.auth_store).parent/('release-'+digest(inspection_id)[:24]+'.json')
 if marker.exists():raise HostBlocked('RELEASE_ALREADY_ATTEMPTED_INSPECT_RECEIPT')
 lifecycle=['PROPOSED','REQUESTED','SCHEDULED','IN_PROGRESS','COMPLETED']
 if repo.get_node(inspection_id,'Inspection').properties['status'] not in lifecycle[:-1]:raise HostBlocked('INSPECTION_NOT_RELEASABLE')
 from app.services.demo.definitions import load
 world=load()[case.scenario]
 samples=world.release[case.issue]
 # Only the targets the agent actually requested receive matching field results.
 observations=[]
 for asset in sorted(assets):
  if case.scenario=='S03' and asset.startswith('PIPE'):
   rows=[{'code':'PRESSURE_TEST_NORMAL','statement':'Independent synthetic utility pressure test normal','result':'OBSERVED','value':None,'unit':None}]
  elif case.scenario=='S04' and asset.startswith('ROAD'):
   rows=[{'code':c,'statement':'Explicit synthetic road field survey: '+c,'result':'OBSERVED','value':None,'unit':None} for c in ['SUBGRADE_FAILURE_OBSERVED','STRUCTURAL_TEST_FAILED','SUBGRADE_REPAIR_SAFETY_REVIEWED']]
  elif (case.scenario=='S04' and asset.startswith('PIPE')) or case.scenario!='S04':
   rows=[s.model_dump(mode='json') for s in samples]
   safety={'S01':'DRAIN_CLEARANCE_SAFETY_REVIEWED','S03':'SUBGRADE_REPAIR_SAFETY_REVIEWED','S04':'UTILITY_SAFETY_REVIEWED','S05':'PICKUP_RECOVERY_SAFETY_REVIEWED'}.get(case.scenario)
   if safety:rows.append({'code':safety,'statement':'Explicit synthetic field safety review: '+safety,'result':'OBSERVED','value':None,'unit':None})
  else:raise HostBlocked('INSPECTION_TARGET_UNSUPPORTED')
  observations.extend({'asset_id':asset,'method':'SYNTHETIC_PRESENTER_FIELD_SURVEY',**row} for row in rows)
 write_private(marker,{'status':'DISPATCHING','inspection_id':inspection_id,'investigation_id':case_id})
 field_token=auth.login(who,passwords[who]);review_token=auth.login('OP-ANALYST',passwords['OP-ANALYST'])
 try:
  field,reviewer=auth.resolve(field_token),auth.resolve(review_token)
  for status in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
   current=repo.get_node(inspection_id,'Inspection')
   if lifecycle.index(current.properties['status'])>=lifecycle.index(status):continue
   at=utc_now()
   ev.execute({'operation':'transition_inspection','request_id':'DEMO-'+digest([inspection_id,status])[:32],'inspection_id':inspection_id,'expected_hash':current.content_hash,'status':status,**({'scheduled_at':at} if status=='SCHEDULED' else {})},field)
  current=repo.get_node(inspection_id,'Inspection');at=utc_now()
  request='DEMO-'+digest([inspection_id,'REPORT'])[:32]
  result=EvidenceService(repo,clock=lambda:at).execute({'operation':'report_inspection','request_id':request,'inspection_id':inspection_id,'expected_hash':current.content_hash,'source_id':'DEMO-synthetic-field-team','record_id':inspection_id,'source_kind':'SYNTHETIC','observations':[{**row,'observed_at':at} for row in observations],'review':{'reviewer_id':reviewer.id,'role':'ANALYST','reviewed':True,'reason':'Independent authenticated review of explicitly synthetic presenter observations'},'attribution':{'incident_ids':[case.incident_id],'mode':'OCCURRENCE','rationale':'Direct synthetic inspection of the active demonstration episode','basis_evidence_ids':[]}},field)
  if case.scenario in {'S05','S06'}:
   from app.services.demo.service_history import release as service_release
   from app.services.operations.service import Operations
   from app.services.planning.service import PlanningService
   from app.events.service import Delivery
   from app.services.http.service import Services
   from app.active import load as profile_load
   profile=profile_load(config.profile)
   services=Services(profile,config.profile,repo,auth,Operations(PlanningService(repo),auth),Delivery(repo,lambda:at),lambda:at)
   service_release(services,case.scenario,'PRIMARY',{'investigation_id':case_id,'incident_id':case.incident_id,'asset_id':next(iter(assets))},result.entity_id,field,reviewer,request)
  # Receipt remains separate: a DISPATCHING marker never permits redispatch.
  receipt={'status':'COMMITTED','inspection_id':inspection_id,'evidence_id':result.entity_id,'investigation_id':case_id,'source_kind':'SYNTHETIC','reviewed_by':reviewer.id,'inspector_id':field.id}
  write_private(marker.with_name(marker.stem+'-receipt.json'),receipt)
  return receipt
 finally:
  auth.logout(field_token);auth.logout(review_token)
