"""Authored synthetic source records, not operational execution or hidden answers."""
from tests.schema_examples import common,asset,edge,NOW
from tests.graph_fixtures import evidence

CLOCK='2026-10-18T12:00:00Z'

def payload(issue='WATERLOGGING',ref='report-1',**changes):
    return {'issue_type':issue,'description':'Synthetic reported condition; cause unverified',
        'source_id':'fixture-portal','external_record_id':ref,'source_channel':'TEST',
        'reported_at':'2026-10-18T05:00:00Z','occurred_at':'2026-10-18T04:00:00Z','location_id':'L1',
        'asset_ids':[{'WATERLOGGING':'D1','ROAD_DAMAGE':'R1','WASTE_ACCUMULATION':'W1'}[issue]],**changes}


def populate(repo,history=False):
    evidence(repo,'EV');evidence(repo,'EV-INS')
    for id in ['L1','L2','L3']:
        repo.create_node('Location',{**common(id),'name':'Synthetic equal-coordinate locations','latitude':12.0,'longitude':77.0})
    for kind,id,loc in [('DrainSegment','D1','L1'),('DrainSegment','D2','L2'),('RoadSegment','R1','L1'),('WaterPipe','P1','L1'),('WasteCollectionPoint','W1','L1')]:
        repo.create_node(kind,asset(kind,id))
        repo.create_relationship('LOCATED_AT',id,loc,{**edge('LOC-'+id),'valid_from':NOW,'source_evidence_id':'EV'})
    if history:populate_history(repo)


def populate_history(repo):
    repo.create_node('Inspection',{**common('INS'),'inspection_type':'ROAD','status':'COMPLETED','requested_at':NOW,'completed_at':NOW})
    repo.create_relationship('INSPECTS','INS','R1',{**edge('INS-R1'),'source_evidence_id':'EV-INS'})
    repo.create_relationship('PRODUCED','INS','EV-INS',edge('PRODUCED-EV'))
    repo.create_node('ActionTask',{**common('TASK'),'action_type':'HISTORICAL_TEST','status':'COMPLETED','priority':'HIGH'})
    repo.create_node('WorkOrder',{**common('ORDER'),'status':'COMPLETED','execution_mode':'SIMULATED','plan_version':1,'idempotency_key':'AUTHORED-HISTORY'})
    outcome=common('OUTCOME');outcome.pop('updated_at')
    repo.create_node('InterventionOutcome',{**outcome,'assessment_status':'HISTORICAL','evaluated_at':NOW,'result':'ACTION_COMPLETED'})
    for kind,s,t,id in [('TARGETS','TASK','R1','TARGET'),('IMPLEMENTS','ORDER','TASK','IMPL'),('RESULTED_IN','ORDER','OUTCOME','OUT')]:repo.create_relationship(kind,s,t,{**edge(id),'source_evidence_id':'EV'})
    repo.create_node('CollectionRoute',{**common('ROUTE'),'route_code':'SYNTHETIC','operational_status':'ACTIVE'})
    repo.create_node('ServiceSchedule',{**common('SCHEDULE'),'service_type':'WASTE','timezone':'Asia/Kolkata','schedule_spec':'local07:00; source alias retained','valid_from':NOW})
    for kind,s,t,id in [('COLLECTED_BY','W1','ROUTE','ROUTE-W1'),('HAS_SCHEDULE','ROUTE','SCHEDULE','SCHED-ROUTE')]:repo.create_relationship(kind,s,t,{**edge(id),'valid_from':NOW,'association_status':'VERIFIED','source_evidence_id':'EV'})
    for i,status in enumerate(['MISSED','PARTIAL','COMPLETED']):
        id='PICKUP-'+status;at=f'2026-10-18T03:{i:02}:00Z'
        props={**common(id),'route_id':'ROUTE','scheduled_at':at,'status':status,'source_record_id':'SYNTHETIC-'+id}
        if status!='MISSED':props['actual_at']=at
        repo.create_node('PickupExecution',props)
        repo.create_relationship('PICKUP_FOR',id,'W1',{**edge('FOR-'+id),'source_evidence_id':'EV'})
