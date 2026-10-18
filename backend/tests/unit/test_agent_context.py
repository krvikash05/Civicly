"""Deterministic size/provenance measurements, not model tokens or live AI quality."""
import copy,json
from pathlib import Path
import pytest
from app.agents.context import build
from app.agents.models import InvestigationState
from app.agents.spending import Pricing


def fixture(issue):
    state=InvestigationState(graph='civicly_b10_test_'+'a'*32,investigation_id='INV',thread_id='T',problem_cluster_id='C',incident_ids=['I'],asset_ids=['A'],issue=issue,graph_revision=100,inventory_hash='hash',as_of='2026-10-18T02:00:00Z')
    report={'inspection_id':'INS','reviewed_by':'SYNTHETIC-ENGINEER','method':'INDEPENDENT_FIELD_TEST','incident_ids':['I'],'observations':[{'code':'CONTRARY','evidence_id':'NEG','observed_at':state.as_of,'description':'Synthetic distinct negative finding '+('measurement '*40)}]}
    hist=[]
    for n in range(8):
        hist.append({'id':'AS-'+str(n),'assessment':'CONTRADICTED','assessed_at':state.as_of,'graph_revision':n+1,'source_graph_revision':n,'as_of':state.as_of,'rule_version':2,'format_version':2,'previous_assessment_id':'AS-'+str(n-1),
            'classification':{'uses':[{'evidence_id':'NEG','category':'REVIEWED_CONTRADICTION','incident_ids':['I'],'reason':'independent dated measurement'},{'evidence_id':'OLD','category':'EXCLUDED','reason':'outside incident episode'},{'evidence_id':'CTX','category':'CONTEXT','reason':'context alone is not causal support'},{'evidence_id':'UNREVIEWED','category':'UNREVIEWED_SUPPORT','reason':'requires review'}]},
            'evidence_references':[{'id':'NEG','content_hash':'h','source_record_id':'report-1','observed_at':state.as_of,'recorded_at':state.as_of,'basis':'OBSERVED','report':report}],
            'supporting_evidence_ids':[],'contradicting_evidence_ids':['NEG'],'excluded_evidence_ids':['OLD'],'missing_evidence':['pressure test'],'paths':[{'id':'PATH','edge_ids':['E'],'association_status':'CANDIDATE','valid_to':'2026-10-17T00:00:00Z'}],'path_ids':['PATH'],'truncated':True,'search_limited':True,'reservations':['No inference beyond bounded search']})
    hs=[{'id':'H','definition':{'cause_code':'POSSIBLE'},'assessments':hist}]
    node={'id':'NEG','properties':{'summary':'Synthetic source '+('raw evidence '*200)}}
    for n in range(10):state.observations.append({'status':'PARTIAL','execution_id':'X'+str(n),'graph_revision':100,'as_of':state.as_of,'source_evidence_ids':['NEG'],'search_limited':True,'truncated':True,'data':{'nodes':[node],'edges':[],'paths':[]},'evidence_gaps':['bounded negative is not absence'],'maintenance_records':[{'event_id':'NEG-EVENT','source_evidence_ids':['NEG'],'negative':True,'valid_from':state.as_of}]})
    shared={'type':'object','properties':{str(n):{'type':'string','description':'Required validated field '+('explanation '*10)} for n in range(30)}}
    cat=[{'name':'safe::tool_'+str(n),'description':'Validated approved tool','input_schema':shared} for n in range(16)]
    return state,hs,cat

@pytest.mark.parametrize('issue',['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION'])
def test_compaction_keeps_critical_history_and_all_tool_schemas(issue):
    state,hs,cat=fixture(issue);before=copy.deepcopy(hs)
    c=build(state,hs,cat,{}, {'PROPOSE':{'nested':{'canonical':'unchanged'}}},['DEP'])
    assert hs==before and len(c['catalog'])==16 and len(c['tool_schemas'])==1
    assert all(c['tool_schemas'][t['input_schema_ref']]==original['input_schema'] for t,original in zip(c['catalog'],cat))
    assert c['controlled_action_schemas']['PROPOSE']['nested']['canonical']=='unchanged'
    for original,material in zip(hs[0]['assessments'][:-1],c['hypotheses'][0]['historical_material']):
        for key in ['classification','paths','reservations','excluded_evidence_ids','contradicting_evidence_ids','as_of','source_graph_revision','truncated']:assert material[key]==original[key]
        ref=material['evidence_references'][0];assert c['facts'][ref['report']['fact_ref']]==original['evidence_references'][0]['report']
    assert all(c['facts'][row['result']['maintenance_records'][0]['fact_ref']]==state.observations[0]['maintenance_records'][0] for row in c['material_observations'])
    assert len(c['material_observations'])==10 and all(row['result']['evidence_gaps'] for row in c['material_observations'])
    old={'state':state.model_dump(mode='json'),'hypotheses':hs,'catalog':cat,'policies':{},'controlled_action_schemas':c['controlled_action_schemas'],'departments':['DEP']}
    sizes={name:len(json.dumps(value,separators=(',',':')).encode()) for name,value in [('before',old),('after',c)]}
    assert sizes['after']<sizes['before']*.65
    p=Pricing();proof={'issue':issue,'fixture':'Authored complex 8-assessment/10-read/16-tool projection; not live reasoning','json_utf8_bytes':sizes,'reduction_fraction':1-sizes['after']/sizes['before'], 'estimate_scope':'Context JSON plus framing/output allowance only; production also reserves prompt/selection-schema bytes. Not tokenizer or billed usage','simulated_context_allocation_nusd':{k:p.estimate(v,4096) for k,v in sizes.items()},'actual_billed_usage':'NOT RUN','all_tools_retained':16,'history_records_in_projection':8}
    Path('/tmp/civicly-b10o-context-'+issue+'.json').write_text(json.dumps(proof,indent=2)+'\n')
