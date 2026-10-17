"""Small explicit B03 graphs, never the city fixture or evaluation dataset."""
from tests.schema_examples import NOW, common, asset, edge


def evidence(repo, id='EV', **overrides):
    return repo.create_node('Evidence', {**common(id), 'evidence_type': 'INSPECTION_REPORT',
        'summary': 'Synthetic inspection', 'reliability': 'VERIFIED', 'recorded_at': NOW,
        'observed_at': NOW, 'source_kind': 'SYNTHETIC', 'source_record_id': 'test-record', **overrides})


def task(repo, id):
    return repo.create_node('ActionTask', {**common(id), 'action_type': 'TEST', 'status': 'PENDING', 'priority': 'HIGH'})


def fixture_graph(repo):
    evidence(repo)
    evidence(repo, 'COUNTER')
    for label, id in [('DrainSegment','D1'),('DrainSegment','D2'),('DrainInlet','D3'),
                      ('WasteCollectionPoint','W'),('RoadSegment','R'),('RoadSegment','NEARBY')]:
        repo.create_node(label, asset(label,id))
    for id in ('LW','LR','LN'):
        repo.create_node('Location', {**common(id), 'name': 'Same coordinates, explicit connections only',
                                     'latitude': 12.0, 'longitude': 77.0})
    for id, issue in [('I1','WATERLOGGING'),('I2','ROAD_DAMAGE'),('I3','WASTE_ACCUMULATION')]:
        repo.create_node('Incident', {**common(id), 'issue_type': issue, 'subtype': 'TEST', 'status': 'OPEN',
                                      'severity': 'HIGH', 'started_at': NOW})
    repo.create_node('Department', {**common('DEP'), 'name':'Synthetic department','department_type':'DRAINAGE'})
    repo.create_node('CollectionRoute', {**common('ROUTE'), 'route_code':'TEST','operational_status':'ACTIVE'})
    repo.create_node('ServiceSchedule', {**common('SCHEDULE'),'service_type':'WASTE','timezone':'UTC',
                                         'schedule_spec':'TEST','valid_from':NOW})
    repo.create_node('Inspection', {**common('INS'), 'inspection_type':'DRAIN','status':'COMPLETE','requested_at':NOW})
    repo.create_node('Investigation', {**common('INV'),'status':'OPEN','priority':'HIGH','opened_at':NOW})
    repo.create_node('Hypothesis', {**common('H'),'cause_code':'TEST','statement':'Test hypothesis','status':'OPEN'})
    assessment = common('HA'); assessment.pop('updated_at')
    repo.create_node('HypothesisAssessment', {**assessment, 'assessment':'INCONCLUSIVE','rationale':'Test','assessed_at':NOW})
    task(repo,'T1'); task(repo,'T2'); task(repo,'T3')
    repo.create_node('WorkOrder', {**common('WO'),'execution_mode':'SIMULATED','status':'COMPLETE',
                                  'plan_version':1,'idempotency_key':'TEST-WO'})
    outcome=common('OUT'); outcome.pop('updated_at')
    repo.create_node('InterventionOutcome',{**outcome,'assessment_status':'TEST','evaluated_at':NOW,'result':'INCONCLUSIVE'})
    relations = [('DRAINS_TO','D1','D2'),('DRAINS_TO','D2','D3'),('AFFECTS','I1','D1'),('AFFECTS','I2','D2'),
        ('AFFECTS','I3','W'),('LOCATED_AT','W','LW'),('LOCATED_AT','R','LR'),('LOCATED_AT','NEARBY','LN'),
        ('SERVES','D1','LW'),('SERVES','D3','LR'),('OCCURRED_AT','I1','LW'),('OCCURRED_AT','I2','LW'),
        ('MAINTAINED_BY','D1','DEP'),('COLLECTED_BY','W','ROUTE'),('HAS_SCHEDULE','ROUTE','SCHEDULE'),
        ('INSPECTS','INS','D1'),('PRODUCED','INS','EV'),('TARGETS','T1','D1'),('IMPLEMENTS','WO','T1'),
        ('RESULTED_IN','WO','OUT'),('PROPOSES','INV','H'),('HAS_ASSESSMENT','H','HA'),
        ('SUPPORTED_BY','HA','EV'),('CONTRADICTED_BY','HA','COUNTER'),('DEPENDS_ON','T1','T2'),
        ('DEPENDS_ON','T2','T3'),('ASSIGNED_TO','T1','DEP')]
    for index,(kind,source,target) in enumerate(relations):
        props = {**edge('E'+str(index)), 'valid_from':NOW}
        if kind in repo.policy['verified_associations']:
            props.update(association_status='VERIFIED',source_evidence_id='EV')
        repo.create_relationship(kind,source,target,props)
    return repo
