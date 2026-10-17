"""Purpose-built evidenced B05 test network; never municipal source or oracle data."""
from tests.schema_examples import common as base_common,asset as base_asset,edge as base_edge
from app.graph.models import digest

NOW='2026-09-01T00:00:00Z'
AS_OF='2026-10-17T23:00:00Z'


def common(id):return {**base_common(id),'created_at':NOW,'updated_at':NOW}
def asset(kind,id):return {**base_asset(kind,id),**common(id)}
def edge(id):return {**base_edge(id),'created_at':NOW}
def task(repo,id):return repo.create_node('ActionTask',{**common(id),'action_type':'CONTROLLED','status':'PENDING','priority':'HIGH'})
def evidence(repo,id,**overrides):
    return repo.create_node('Evidence',{**common(id),'evidence_type':'INSPECTION_REPORT',
        'summary':'Explicit purpose-built synthetic test inspection, not municipal evidence',
        'reliability':'VERIFIED','recorded_at':NOW,'observed_at':NOW,'source_kind':'SYNTHETIC',
        'source_record_id':'b05-controlled-fixture',**overrides})


def network(repo):
    evidence(repo,'EV',source_record_id='b05-controlled-fixture#dated-inspection')
    evidence(repo,'EV-CANDIDATE',reliability='UNVERIFIED',source_record_id='b05-controlled-fixture#unverified-claim')
    for label,id in [('DrainSegment',i) for i in ('D1','D2','D3','D4','D5','NEARBY','EXPIRED')]+[('WaterPipe','PIPE'),('RoadSegment','ROAD'),('WasteCollectionPoint','WASTE')]:
        repo.create_node(label,asset(label,id))
    for id in ('L','LN'):
        repo.create_node('Location',{**common(id),'name':'Purpose-built same-coordinate negative control','latitude':12.0,'longitude':77.0})
    repo.create_node('Zone',{**common('Z'),'name':'Controlled zone','zone_type':'DEMO'})
    repo.create_node('CollectionRoute',{**common('ROUTE'),'route_code':'B05','operational_status':'ACTIVE'})
    for id,kind,date in [('OLD','WATERLOGGING',NOW),('DEPENDENT-CASE','ROAD_DAMAGE','2026-09-05T00:00:00Z'),('SEED','WATERLOGGING','2026-09-10T00:00:00Z'),('LATER','WATERLOGGING','2026-09-20T00:00:00Z'),('DISTANT','WASTE_ACCUMULATION',NOW)]:
        repo.create_node('Incident',{**common(id),'issue_type':kind,'subtype':'CONTROLLED','started_at':date,'status':'OPEN','severity':'HIGH'})
    repo.create_node('ProblemCluster',{**common('CLUSTER'),'title':'Controlled recurring reports','pattern_type':'RECURRENT','status':'OPEN','first_seen_at':NOW})
    repo.create_node('ResolutionPlan',{**common('PLAN'),'version':1,'status':'DRAFT','plan_hash':digest('fixture-plan')})
    for id in ('T1','T2','T3'):task(repo,id)
    repo.create_node('Inspection',{**common('INS'),'inspection_type':'CONTROLLED','status':'COMPLETED','requested_at':NOW,'completed_at':NOW})
    repo.create_node('WorkOrder',{**common('WO'),'execution_mode':'SIMULATED','status':'COMPLETED','plan_version':1,'idempotency_key':'B05-FIXTURE'})
    p=common('OUT');p.pop('updated_at')
    repo.create_node('InterventionOutcome',{**p,'assessment_status':'CONTROLLED','evaluated_at':NOW,'result':'INCONCLUSIVE'})
    relations=[('DRAINS_TO','D1','D2','D12'),('DRAINS_TO','D2','D3','CUT'),('DRAINS_TO','D4','D3','D43'),('DRAINS_TO','D3','D5','D35'),
       ('UNDERLIES','PIPE','ROAD','PIPE-ROAD'),('COLLECTED_BY','WASTE','ROUTE','WASTE-ROUTE'),
       ('LOCATED_AT','D1','L','LOC-D1'),('LOCATED_AT','NEARBY','L','LOC-N'),('IN_ZONE','L','Z','L-Z'),
       ('AFFECTS','OLD','D1','A-OLD'),('AFFECTS','DEPENDENT-CASE','D2','A-DEP'),('AFFECTS','SEED','D1','A-SEED'),('AFFECTS','LATER','D1','A-LATER'),('AFFECTS','DISTANT','NEARBY','A-DISTANT'),
       ('OCCURRED_AT','OLD','L','O-OLD'),('OCCURRED_AT','DEPENDENT-CASE','L','O-DEP'),('OCCURRED_AT','SEED','L','O-SEED'),('PART_OF','OLD','CLUSTER','P-OLD'),('PART_OF','SEED','CLUSTER','P-SEED'),
       ('HAS_TASK','PLAN','T1','PLAN-T1'),('DEPENDS_ON','T1','T2','DEP12'),('DEPENDS_ON','T2','T3','DEP23'),
       ('TARGETS','T1','D1','TARGET'),('IMPLEMENTS','WO','T1','IMPL'),('RESULTED_IN','WO','OUT','RESULT'),
       ('INSPECTS','INS','D1','INSPECT'),('PRODUCED','INS','EV','PROOF')]
    for kind,s,t,id in relations:
        props={**edge(id),'valid_from':NOW,'source_evidence_id':'EV'}
        if kind in repo.policy['verified_associations']:props['association_status']='VERIFIED'
        repo.create_relationship(kind,s,t,props)
    repo.create_relationship('DRAINS_TO','D1','EXPIRED',{**edge('EXPIRED-LINK'),'association_status':'VERIFIED','source_evidence_id':'EV','valid_from':NOW,'valid_to':'2026-09-02T00:00:00Z'})
    return repo
