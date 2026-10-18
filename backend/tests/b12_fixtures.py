"""Authored planning inputs, never expected hidden scenario answers or live AI."""
import asyncio
from app.services.planning.models import PlanDraft
from app.services.planning.storage import PlanMigration
from app.services.planning.service import PlanningService
from app.services.evidence.reader import Reader
from app.active import active_scope
from app.memory.models import sources
from tests.b10or2_fixtures import prepare,ALT
from tests.b09_fixtures import Fixture,propose,assess
from tests.schema_examples import common,edge
ISSUES=['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']
DEPT={'WATERLOGGING':'DEPT-DRAIN','ROAD_DAMAGE':'DEPT-ROAD','WASTE_ACCUMULATION':'DEPT-SAN'}
ASSET={'WATERLOGGING':'D1','ROAD_DAMAGE':'R1','WASTE_ACCUMULATION':'W1'}
REQUIRED={'WATERLOGGING':['COMPARABLE_FOLLOWUP_RAINFALL','FOLLOWUP_WATERLOGGING'],'ROAD_DAMAGE':['FOLLOWUP_PAVEMENT','WEAR_EXPOSURE'],'WASTE_ACCUMULATION':['SCHEDULED_PICKUPS','ACTUAL_PICKUPS','REACCUMULATION_WINDOW']}
def sample():
 citation={'source_document_id':'D001','source_version':1,'canonical_document_id':'ORG:D001:1','owner_department_id':'DEPT-DRAIN','source_uri':'data/documents/drainage_blockage_sop.md','content_checksum':'a'*64,'quote_excerpt':'Authored synthetic procedure excerpt','passage_location':'chunk:0:00000000-0000-4000-8000-000000000000','chunk_sha256':'b'*64,'confidence_label':'SOURCE_REVIEWED_SYNTHETIC','retrieved_at':'2026-10-18T00:00:00Z','effective_from':'2026-09-01T00:00:00Z'}
 return {'investigation_id':'INV','issue':'WATERLOGGING','version':1,'basis':[{'hypothesis_id':'H1','assessment_id':'A1','reason':'Address a documented uncertainty','addressed':True},{'hypothesis_id':'H2','assessment_id':'A2','reason':'Retain competing mechanism until discriminating evidence','addressed':False}],'evidence_ids':['EV'],
 'tasks':[{'id':'inspect','action_type':'INSPECTION','target_ids':['D1'],'department_id':'DEPT-DRAIN','priority':'HIGH','prerequisites':['Human review and later authorized inspection execution required'],'depends_on':[],'evidence_ids':['EV'],'assessment_ids':['A1'],'procedure_citation':citation,'expected_outcome':'Collect discriminating dated attributed evidence','verification_criteria':'Independent reviewed findings distinguish alternatives','risks':['Reported condition may have another mechanism']}],
 'expected_outcomes':['Clarify mechanism without declaring cause verified'],'risks':['Source guidance is synthetic/proposed'],'uncertainties':['No verified physical cause or completed work inferred'],'monitoring':{'issue':'WATERLOGGING','required_evidence':REQUIRED['WATERLOGGING'],'observation_opportunity':'Suitable comparable rainfall after any later approved work','verification_criteria':'Dated follow-up evidence assesses recurrence under comparable conditions'}}
def prepared(db,tmp_path,memory,issue,*,remedial=False):
 path=tmp_path/'agent.json'
 if remedial:
  from tests.b10_fixtures import create
  from tests.b10or2_fixtures import CAUSE
  from tests.b09_fixtures import report
  from app.services.evidence.policies import POLICIES
  from app.services.planning.policy import ACTIONS
  p,r,clock,receipt,inv=create(db,path,issue);f=Fixture(r,clock,{issue:receipt},p.graph,{})
  with active_scope(p):
   if issue=='ROAD_DAMAGE':r.create_relationship('UNDERLIES','P1','R1',{**edge('B12R-PIPE-ROAD'),'source_evidence_id':'EV','association_status':'VERIFIED'})
   h=propose(f,inv,issue,CAUSE[issue],ref='B12R-supported-cause')
   policy=next(v for v in ACTIONS.values() if v['issue']==issue)
   report(f,inv,ref='B12R-authored-physical-and-safety',codes=POLICIES[issue][CAUSE[issue]]['confirming']+[policy['safety_code']],assets=[ASSET[issue]])
   assess(f,h,ref='B12R-reviewed-support')
 else:
  p,r,clock,receipt,inv,h=prepare(db,path,issue);f=Fixture(r,clock,{issue:receipt},p.graph,{})
 with active_scope(p):
  changes={'asset_ids':['P1'],'topology':{'source_id':'P1','target_id':'R1','operation':'dependencies','max_hops':3}} if issue=='ROAD_DAMAGE' else {}
  second=propose(f,inv,issue,ALT[issue],ref='B12-alternative',**changes);assess(f,second,ref='B12-alternative-assessment')
  histories=[Reader(r,clock()).histories(id)[-1] for id in [h,second]]
  for dept in ['DEPT-DRAIN','DEPT-ROAD','DEPT-WATER','DEPT-SAN','DEPT-COORD']:r.create_node('Department',{**common(dept),'name':dept,'department_type':'ENGINEERING'})
  bindings=[(ASSET[issue],DEPT[issue])]+([('P1','DEPT-WATER')] if issue=='ROAD_DAMAGE' else [])
  for asset,dept in bindings:r.create_relationship('MAINTAINED_BY',asset,dept,{**edge('B12-OWNER-'+asset),'source_evidence_id':'EV','association_status':'VERIFIED'})
 PlanMigration(db,p.graph).apply();value=sample();value.update(investigation_id=inv,issue=issue)
 value['basis']=[{'hypothesis_id':a.hypothesis_id,'assessment_id':a.id,'reason':'Address assessed uncertainty' if i==0 else 'Retain competing assessed alternative','addressed':i==0} for i,a in enumerate(histories)]
 value['evidence_ids']=list(dict.fromkeys(id for a in histories for id in a.supporting_evidence_ids+a.contradicting_evidence_ids));assert value['evidence_ids']
 value['tasks']=[]
 for i,(asset,dept) in enumerate(bindings):
  source=next(s for s in sources() if s.owner_department_id==dept and s.document_id!='D001-PDF');asyncio.run(memory.ingest(source))
  citation=asyncio.run(memory.retrieve(as_of=clock(),document_id=source.document_id))['citations'][0]
  task=sample()['tasks'][0];task.update(id='inspect'+str(i),target_ids=[asset],department_id=dept,evidence_ids=value['evidence_ids'],assessment_ids=[a.id for a in histories],procedure_citation=citation,depends_on=[] if i==0 else ['inspect0'])
  value['tasks'].append(task)
 value['monitoring']={'issue':issue,'required_evidence':REQUIRED[issue],'observation_opportunity':'Comparable rainfall' if issue=='WATERLOGGING' else 'Meaningful scheduled/actual pickup and reaccumulation observation window' if issue=='WASTE_ACCUMULATION' else 'Follow-up pavement after relevant wear exposure','verification_criteria':'Review dated attributed follow-up observations; no opportunity remains unresolved'}
 if remedial:
  from pathlib import Path
  source=next(s for s in sources(Path('data/documents/b12r/manifest.json')) if s.owner_department_id==DEPT[issue])
  asyncio.run(memory.ingest(source))
  citation=asyncio.run(memory.retrieve(as_of=clock(),document_id=source.document_id))['citations'][0]
  support=histories[0].classification.reviewed_support_ids;assert histories[0].assessment in {'SUPPORTED','VERIFIED'} and support
  task=value['tasks'][0];task.update(id='remedy',action_type=source.action_types[0],evidence_ids=support,assessment_ids=[histories[0].id],procedure_citation=citation,
   expected_outcome='Qualified proposal to address '+histories[0].cause_code+'; no performed work or verified resolution',
   remediation={'mode':'SUPPORTED_NOW','conditions':[{'kind':kind,'status':'MET','evidence_ids':support} for kind in ['CAUSAL_INSPECTION','SAFETY_REVIEW']]})
  value['tasks']=[task]
 return p,r,clock,path,inv,PlanDraft.model_validate(value),PlanningService(r,memory,clock=clock)
