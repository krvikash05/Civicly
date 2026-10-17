import pytest
from pydantic import ValidationError

from app.graph.models import QueryRequest, NodeRecord
from app.graph.queries import ReadLimits
from app.graph.repository import intersection, interval
from tests.schema_examples import NOW


@pytest.mark.parametrize('change',[{'template':'MATCH (n) RETURN n'},{'limit':101},{'limit':True},
    {'max_hops':0},{'max_hops':7},{'timeout_ms':1001},{'as_of':'2026-10-17'},
    {'as_of':'2026-10-17T00:00:00+00:00'},{'cypher':'CREATE (:Bad)'},{'incident_ids':tuple(str(i) for i in range(51))}])
def test_typed_requests_reject_unknown_unbounded_or_coerced_input(change):
    with pytest.raises((ValidationError,ValueError)):
        QueryRequest(**{'template':'drainage_paths','id':'A','as_of':NOW,**change})


def test_interval_boundaries_and_unbounded_history():
    one=interval({'valid_from':NOW,'valid_to':'2026-10-18T00:00:00Z'})
    two=interval({'valid_from':'2026-10-18T00:00:00Z'})
    assert intersection(one,two) is None
    assert intersection(one,(None,None))==one
    assert intersection((None,None),(None,None))==(None,None)


def test_serializable_hashes_and_configured_hard_caps():
    a=NodeRecord(id='A',kind='Location',labels=('Location',),properties={'id':'A','x':1})
    b=NodeRecord(id='A',kind='Location',labels=('Location',),properties={'x':1,'id':'A'})
    assert a.content_hash==b.content_hash and len(a.content_hash)==64
    assert '"id":"A"' in a.model_dump_json()
    with pytest.raises(ValidationError): ReadLimits(max_edges=201)
