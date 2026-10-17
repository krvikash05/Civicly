import pytest

from app.graph.migration import MigrationError, MigrationRunner
from app.graph.repository import GraphRepository, PreconditionFailed
from app.graph.targets import is_allowed_graph_target, is_disposable_graph, new_test_graph_name
from app.graph.models import QueryRequest
from tests.schema_examples import NOW


@pytest.mark.parametrize('milestone',[2,3,4,10,25])
def test_reusable_disposable_names(milestone):
    name=new_test_graph_name(milestone)
    assert is_disposable_graph(name) and is_allowed_graph_target(name)
    assert name.startswith(f'civicly_b{milestone:02d}_test_')
    assert is_allowed_graph_target('civicly_knowledge')
    assert not is_disposable_graph('civicly_knowledge')


@pytest.mark.parametrize('name',[
    None,123,False,'','civicly_b01_runtime','civicly_docs','civicly_checkpoints',
    'civicly_knowledge_backup','civicly_knowledge\n','CIVICLY_KNOWLEDGE',
    'civicly_b04_test_'+'0'*32,'civicly_b04_test_'+'a'*32,
    'civicly_b4_test_123','civicly_b04_test_'+'g'*32,
    'civicly_b01_test_123456781234423482341234567890ab',
    'civicly_b00_test_123456781234423482341234567890ab',
    'civicly_b26_test_123456781234423482341234567890ab',
    'other_production_graph','../civicly_knowledge',
])
def test_unauthorized_targets_refused_before_client_access(name):
    assert not is_allowed_graph_target(name)
    with pytest.raises(MigrationError,match='target'): MigrationRunner(object(),name)
    with pytest.raises(PreconditionFailed,match='target'): GraphRepository(object(),name)


@pytest.mark.parametrize('milestone',[0,1,26,99,True,'04',None])
def test_bad_milestone_cannot_generate_name(milestone):
    with pytest.raises(ValueError): new_test_graph_name(milestone)


def test_default_total_budget_supports_cross_category_minimum():
    request=QueryRequest(template='cross_category_paths',id='W',as_of=NOW)
    assert request.max_hops==6
