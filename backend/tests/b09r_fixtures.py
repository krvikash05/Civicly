"""Controlled B08 source-copy fixtures and attributed B09 reports; no city mutations."""
from datetime import datetime
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.graph.targets import new_test_graph_name
from app.graph.analysis.counterfactual import capture
from app.services.complaints import ComplaintService
from app.services.evidence import Actor
from tests.b08_fixtures import payload
from tests.b09_fixtures import request, advance_inspection


def at(f, value):
    f.clock.value=datetime.fromisoformat(value.replace('Z','+00:00'))


def mirror(source, destination):
    snapshot=capture(source)
    for n in sorted(snapshot.nodes,key=lambda n:(n.kind!='Evidence',n.id)):
        existing=destination._node_optional(n.id)
        if not existing:
            destination.create_node(n.kind,n.properties)
        elif existing.content_hash!=n.content_hash:
            changes={k:v for k,v in n.properties.items() if k not in {'id','created_at','municipality_id','schema_version'} and existing.properties.get(k)!=v}
            assert set(existing.properties)<=set(n.properties), 'No fixture property removal'
            destination.update_node(n.id,changes,expected_hash=existing.content_hash)
    for e in snapshot.edges:
        existing=destination._edge_optional(e.id)
        if not existing:
            destination.create_relationship(e.kind,e.source,e.target,e.properties)
        elif existing.content_hash!=e.content_hash:
            raise AssertionError('Fixture does not conceal changed relationship policy')
    assert capture(destination).records==snapshot.records


def source_copy(f, *,issue,ref,occurred,reported):
    """Intake into a newly owned B08 graph; explicitly copy its delta back to isolated B09."""
    db=f.repo.client;name=new_test_graph_name(8)
    try:
        MigrationRunner(db,name).apply();source=GraphRepository(db,name,lease_seconds=30)
        mirror(f.repo,source)
        result=ComplaintService(source,clock=lambda:reported).intake(payload(issue,ref=ref,
            occurred_at=occurred,reported_at=reported,event_reference='distinct-'+ref))
        mirror(source,f.repo)
        return result
    finally:
        if name in db.list_graphs():db.select_graph(name).delete()


def attributed_report(f, inv, ref, *, codes, attribution, assets=None):
    assets=assets or ['R1']
    ins=request(f,inv,'request-'+ref,assets)
    for state in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
        advance_inspection(f,ins,state)
    f.clock.advance()
    return f.service.execute({'operation':'report_inspection','request_id':'report-'+ref,'inspection_id':ins,
        'expected_hash':f.repo.get_node(ins).content_hash,'source_id':'independent-'+ref,'record_id':'record-'+ref,
        'observations':[{'asset_id':assets[0],'code':code,'statement':'Authored attributed observation '+code,
            'method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':f.clock()} for code in codes],
        'review':{'reviewer_id':'independent-reviewer','role':'ANALYST','reviewed':True,
                  'reason':'Reviewed source basis and named occurrence attribution'},'attribution':attribution},
        Actor(id='inspector-'+ref,role='DEPARTMENT_LEAD',department_id='DEP'))
