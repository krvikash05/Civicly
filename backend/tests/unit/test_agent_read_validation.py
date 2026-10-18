"""Read contract failures reproduced without dispatch; mocked provider, no live API."""
import asyncio,copy,json
from types import SimpleNamespace as NS
import pytest
from app.agents.models import Selection
from app.agents.selection_validation import validate_read,SelectionInputError
from app.agents.mcp import Tools
from app.graph.models import digest
from app.mcp.civicly.contracts import READ
from tests.b10_fixtures import choose
from tests.unit.test_ai_provider_recovery import model
import httpx


def context():
 official=NS(operator_inventory=[{'name':'query_graph_readonly','description':'read'}],tools=lambda:[{'name':'query_graph_readonly'}])
 rows=Tools(official,NS(tools=lambda:[{'name':'civicly::retrieve_external_evidence','description':'read','input_schema':READ['retrieve_external_evidence']['input_schema']}]),None,[],'SOURCE').catalog()
 return {'state':{'asset_ids':['ASSET'],'as_of':'2026-10-18T15:00:00Z'},'catalog':[{'name':r['name'],'input_schema_ref':digest(r['input_schema'])} for r in rows],'tool_schemas':{digest(r['input_schema']):r['input_schema'] for r in rows}}


def selection(args,name='official::query_graph_readonly'):
 return Selection.model_validate(choose('READ',args,name))


@pytest.mark.parametrize('args',[
 {'id':'ROAD','sample_size':20}, {'template':'node','id':'ROAD','as_of':'2026-10-18T14:00:00Z'},
 {'template':'drainage_edges','id':'DRAIN'}, {'template':'node','id':'ROAD','query':'secret body must not be echoed'},
 {'template':'node','id':'ROAD','sample_size':20}, {'template':'node','id':None}])
def test_bad_official_arguments_rejected_without_echo(args):
 with pytest.raises(SelectionInputError) as error:validate_read(selection(args),context())
 assert 'secret body' not in str(error.value)


def test_undiscovered_tool_and_asset_used_as_location_rejected():
 with pytest.raises(SelectionInputError,match='NOT_DISCOVERED'):validate_read(selection({},'invented'),context())
 args={'location_id':'ASSET','evidence_type':'RAINFALL','from_time':'2026-10-18T13:00:00Z','to_time':'2026-10-18T14:00:00Z'}
 with pytest.raises(SelectionInputError,match='LOCATION_TYPE'):validate_read(selection(args,'civicly::retrieve_external_evidence'),context())
 args['location_id']='ACTUAL-LOCATION';validate_read(selection(args,'civicly::retrieve_external_evidence'),context())
 args['to_time']='2026-10-18T16:00:00Z'
 with pytest.raises(SelectionInputError,match='TIME_WINDOW'):validate_read(selection(args,'civicly::retrieve_external_evidence'),context())


def test_valid_arguments_not_rewritten_and_legacy_schema_also_checked():
 c=context();before=copy.deepcopy(c);s=selection({'template':'node','id':'ROAD'});validate_read(s,c)
 assert c==before and s.arguments=={'template':'node','id':'ROAD'}
 c['tool_schemas'][c['catalog'][0]['input_schema_ref']]['required']=[]
 with pytest.raises(SelectionInputError):validate_read(selection({'id':'ROAD'}),c)


def response(value):
 return httpx.Response(200,json={'modelVersion':'gemini-3.8-flash','usageMetadata':{'promptTokenCount':50,'candidatesTokenCount':20,'totalTokenCount':70},'candidates':[{'content':{'parts':[{'text':json.dumps(value)}]}}]})


def test_provider_repairs_before_dispatch_and_accounts_both_responses(tmp_path):
 bad=choose('READ',{'id':'ROAD','sample_size':20},'official::query_graph_readonly')
 good=choose('READ',{'template':'node','id':'ROAD'},'official::query_graph_readonly')
 m,seen=model(tmp_path,[response(bad),response(good)])
 s,tokens=asyncio.run(m.choose(context(),60000))
 assert s.arguments=={'template':'node','id':'ROAD'} and tokens==140 and len(seen)==2
 assert m.last_usage['requests'][0]['selection_validation']=='INVALID_READ_INPUT'
 assert m.ledger.summary()['uncertain_requests']==0


def test_provider_stops_after_existing_single_repair(tmp_path):
 from app.agents.provider import ProviderError
 bad=choose('READ',{'id':'ROAD'},'official::query_graph_readonly')
 m,seen=model(tmp_path,[response(bad),response(bad)])
 with pytest.raises(ProviderError,match='INVALID_MODEL_OUTPUT'):asyncio.run(m.choose(context(),60000))
 assert len(seen)==2 and m.ledger.summary()['uncertain_requests']==0
