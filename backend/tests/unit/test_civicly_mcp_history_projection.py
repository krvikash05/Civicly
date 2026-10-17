"""Pure projection/contract checks with small structural fakes, not DB/MCP proof."""
from types import SimpleNamespace as S
import pytest
from app.mcp.civicly.service import CivicReadService
from app.mcp.civicly.contracts import context,validate,READ


@pytest.mark.parametrize('record,expected',[
    ('INS',['EV-INS']),('WO',['EV-ASSIGN']),
    ('OUT',['EV-ASSIGN','EV-OUT']),('UNLINKED',[])])
def test_maintenance_evidence_follows_event_prefix_not_other_events(record,expected):
    kinds={'ASSET':'RoadSegment','INS':'Inspection','WO':'WorkOrder','OUT':'InterventionOutcome',
           'UNLINKED':'Inspection','EV-INS':'Evidence','EV-OUT':'Evidence'}
    nodes=[S(id=id,kind=kind) for id,kind in kinds.items()]
    edges=[S(id='INSPECTS',kind='INSPECTS',properties={}),
           S(id='PRODUCED',kind='PRODUCED',properties={}),
           S(id='ASSIGN',kind='IMPLEMENTS',properties={'source_evidence_id':'EV-ASSIGN'}),
           S(id='OUTCOME',kind='RESULTED_IN',properties={'source_evidence_id':'EV-OUT'})]
    paths=[S(node_ids=['ASSET','INS','EV-INS'],edge_ids=['INSPECTS','PRODUCED']),
           S(node_ids=['ASSET','WO','OUT'],edge_ids=['ASSIGN','OUTCOME'])]
    result=S(nodes=nodes,edges=edges,paths=paths)
    event=next(n for n in nodes if n.id==record)
    assert CivicReadService.maintenance_evidence(result,event)==expected


def test_work_order_placeholder_limitations_exist_even_before_record_lookup():
    c=context();r=CivicReadService.__new__(CivicReadService).result('get_work_order_status',c,'2026-10-17T00:00:00Z')
    r.update(status='UNAVAILABLE',error={'code':'DATA_UNAVAILABLE','message':'Absent','retryable':False})
    validate(READ['get_work_order_status']['output_schema'],r)
    assert 'not verified empty' in ' '.join(r['data']['gaps'])
