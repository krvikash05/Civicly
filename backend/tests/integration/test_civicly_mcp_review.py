"""Real DB/SDK stdio/broker; test-only source injection, no city mutation.

Bulk fixture creation below is canonical-validated, parameterized TEST setup only,
not a production import path or repository write guarantee/performance shortcut.
"""
import asyncio
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path
import pytest
from mcp import Client,StdioServerParameters
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.graph.schema import Registry
from app.graph.targets import new_test_graph_name
from app.mcp.runtime import ROOT
from app.mcp.civicly.runtime import configure,connections
from app.mcp.civicly.broker import DomainBroker
from app.mcp.civicly.storage import TraceStore
from tests.schema_examples import common,asset,edge

pytestmark=pytest.mark.integration
AS_OF='2026-10-17T12:00:00Z'
OLD='2026-01-01T00:00:00Z'
EARLY='2026-10-01T00:00:00Z'
PROOF=ROOT/'docs/evidence/B07R-runtime-proof.json'


def props(id,**extra):return {**common(id),'created_at':OLD,'updated_at':OLD,**extra}


@pytest.fixture(scope='module')
def history_graph():
    from app.config import Settings
    from app.graph.connection import connect
    with connect(Settings(_env_file='.env')) as db:
        configure(db);name=new_test_graph_name(7)
        registry=Registry();nodes={};relations=[]
        def node(kind,p):registry.validate_node(kind,p);nodes[p['id']]=(kind,p)
        def relation(kind,s,t,id,ev=None,**kw):
            p={**edge(id),'created_at':OLD,**kw}
            if ev:p['source_evidence_id']=ev
            registry.validate_edge(kind,*nodes[s],*nodes[t],p)
            relations.append({'kind':kind,'s':s,'t':t,'props':p})
        for kind,id in [('RoadSegment','R-REVIEW'),('WasteCollectionPoint','W-REVIEW')]:
            node(kind,{**asset(kind,id),'created_at':OLD,'updated_at':OLD})
        node('CollectionRoute',props('ROUTE-REVIEW',route_code='TEST',operational_status='ACTIVE'))
        for id in ['EV-INS-A','EV-INS-B','EV-HISTORY']:
            node('Evidence',props(id,evidence_type='INSPECTION_REPORT',summary='Synthetic B07-R fixture',reliability='VERIFIED',recorded_at=OLD,observed_at=OLD,source_kind='SYNTHETIC'))
        for suffix,date in [('A','2026-10-02T00:00:00Z'),('B','2026-10-03T00:00:00Z')]:
            id='INS-'+suffix;ev='EV-INS-'+suffix
            node('Inspection',props(id,inspection_type='ROAD',status='COMPLETE',requested_at=date,completed_at=date))
            relation('INSPECTS',id,'R-REVIEW','LINK-'+id,ev)
            relation('PRODUCED',id,ev,'PROOF-'+id,ev)
        node('WorkOrder',props('WO-REVIEW',status='PENDING',execution_mode='SIMULATED',plan_version=1,idempotency_key='B07R-WO'))
        # Insert110 older events first, then105 relevant events in reverse order.
        # Second valid record's timestamp uses a fraction to catch naive lexical order.
        # One future event and one event with expired relationship must be excluded.
        for pickup in [True,False]:
            kind='PickupExecution' if pickup else 'AssetConditionSnapshot'
            prefix='P' if pickup else 'C';rel='PICKUP_FOR' if pickup else 'CONDITION_OF';root='W-REVIEW' if pickup else 'R-REVIEW'
            dates=[(f'OLD-{i:03}',OLD) for i in range(110)]
            dates += [(f'NEW-{i:03}',f'2026-10-10T00:{i//60:02}:{i%60:02}Z') for i in reversed(range(105))]
            dates += [('TIE-A','2026-10-10T00:00:00.1Z'),('TIE-B','2026-10-10T00:00:00.100000Z'),('FUTURE','2026-10-18T00:00:00Z'),('EXPIRED',EARLY)]
            for suffix,date in dates:
                id=prefix+'-'+suffix
                extra={'route_id':'ROUTE-REVIEW','scheduled_at':date,'status':'COMPLETED'} if pickup else {'asset_id':root,'evidence_id':'EV-HISTORY','observed_at':date,'condition':'SYNTHETIC'}
                node(kind,props(id,**extra));relation(rel,id,root,'E-'+id,'EV-HISTORY',**({'valid_from':OLD,'valid_to':EARLY} if suffix=='EXPIRED' else {}))
        graph=db.select_graph(name)
        try:
            MigrationRunner(db,name).apply()
            # Static registry-derived labels/kinds, all values parameterized, isolated graph only.
            for kind in sorted({kind for kind,_ in nodes.values()}):
                label=':'.join(registry.labels(kind))
                graph.query(f'UNWIND $rows AS row CREATE (n:{label}) SET n=row',params={'rows':[p for k,p in nodes.values() if k==kind]})
            for kind in sorted({e['kind'] for e in relations}):
                graph.query(f'UNWIND $rows AS row MATCH (s:CivicEntity {{id:row.s}}),(t:CivicEntity {{id:row.t}}) CREATE (s)-[e:{kind}]->(t) SET e=row.props',params={'rows':[e for e in relations if e['kind']==kind]})
            yield name
        finally:
            if name in db.list_graphs():graph.delete()


@asynccontextmanager
async def fixture_broker(name):
    p=StdioServerParameters(command=sys.executable,args=['-m','tests.b07r_server',name],cwd=str(ROOT),env={'PYTHONPATH':str(ROOT/'backend')})
    with connections() as (_,writer,trace_graph):
        async with Client(p,mode='legacy',read_timeout_seconds=8) as client:
            b=DomainBroker(client,TraceStore(writer,trace_graph));await b.discover();yield b


def save(name,result,graph):
    report=json.loads(PROOF.read_text()) if PROOF.exists() else {'evidence_class':'REAL_MCP_DB_WITH_TEST_ONLY_SOURCE_SUBSTITUTION','note':'Fixture source injected only in tests.b07r_server; fixed production context unchanged. Not retained city evidence.','results':{}}
    report['fixture_graph']=graph;report['results'][name]=result
    PROOF.write_text(json.dumps(report,indent=2)+'\n')


def test_maintenance_records_keep_independent_evidence(history_graph):
    async def run():
        async with fixture_broker(history_graph) as b:
            r=await b.call('civicly::get_maintenance_history',{'asset_id':'R-REVIEW','from_time':EARLY,'to_time':AS_OF,'as_of':AS_OF})
            save('maintenance',r,history_graph)
            assert r['status']=='PARTIAL',r['error']
            records={v['record_id']:v['evidence_ids'] for v in r['records']}
            assert records=={'INS-A':['EV-INS-A'],'INS-B':['EV-INS-B']}
            assert set(r['source_evidence_ids'])=={'EV-INS-A','EV-INS-B'}
    asyncio.run(run())


@pytest.mark.parametrize('pickup',[True,False],ids=['pickup','condition'])
def test_history_window_and_stable_order_precede_cap(history_graph,pickup):
    async def run():
        tool='get_pickup_execution_history' if pickup else 'get_road_condition_history'
        root={'collection_point_id':'W-REVIEW'} if pickup else {'road_segment_id':'R-REVIEW'}
        payload='pickup_executions' if pickup else 'road_conditions';prefix='P' if pickup else 'C'
        async with fixture_broker(history_graph) as b:
            r=await b.call('civicly::'+tool,{**root,'days':30,'as_of':AS_OF});save(tool,r,history_graph)
            assert r['status']=='PARTIAL',r['error']
            ids=[n['id'] for n in r[payload]]
            expected=[prefix+'-NEW-000',prefix+'-TIE-A',prefix+'-TIE-B']+[f'{prefix}-NEW-{i:03}' for i in range(1,98)]
            assert ids==expected
            assert r['truncated'] and r['source_evidence_ids']==['EV-HISTORY']
            # Narrow interval has one eligible event after110 unrelated historical rows;
            # no row lookahead truncation and no expiry/future/old leakage.
            narrow=await b.call('civicly::'+tool,{**root,'days':1,'as_of':'2026-10-11T00:01:43Z'})
            save(tool+'-narrow',narrow,history_graph)
            assert [v['id'] for v in narrow[payload]]==[prefix+'-NEW-103',prefix+'-NEW-104']
            assert not narrow['truncated']
            with connections() as (_,writer,name):
                trace=TraceStore(writer,name).get(r['execution_id'])
                assert trace.validated_output and trace.source_evidence_ids==['EV-HISTORY']
    asyncio.run(run())


def test_existing_work_order_reports_operational_retrieval_gaps(history_graph):
    async def run():
        async with fixture_broker(history_graph) as b:
            r=await b.call('civicly::get_work_order_status',{'work_order_id':'WO-REVIEW','as_of':AS_OF});save('work_order',r,history_graph)
            assert r['status']=='PARTIAL' and r['work_order_status']=='PENDING'
            assert r['blocking_task_ids']==[] and r.get('latest_status_event_ids')==[]
            gaps=' '.join(r['data']['gaps'])
            assert 'blocking_task_ids' in gaps and 'latest_status_event_ids' in gaps
            assert 'not verified empty' in gaps and 'B12' in gaps and 'B15' in gaps
    asyncio.run(run())


@pytest.mark.parametrize('pickup',[True,False],ids=['pickup','condition'])
@pytest.mark.parametrize('second,truncated',[(4,True),(5,False)],ids=['101-eligible','100-eligible'])
def test_history_exact_lookahead_boundary(history_graph,pickup,second,truncated):
    async def run():
        tool='get_pickup_execution_history' if pickup else 'get_road_condition_history'
        root={'collection_point_id':'W-REVIEW'} if pickup else {'road_segment_id':'R-REVIEW'}
        payload='pickup_executions' if pickup else 'road_conditions'
        async with fixture_broker(history_graph) as b:
            r=await b.call('civicly::'+tool,{**root,'days':1,'as_of':f'2026-10-11T00:00:{second:02}Z'})
            save(tool+f'-boundary-{second}',r,history_graph)
            assert r['status']=='PARTIAL' and len(r[payload])==100
            assert r['truncated']==truncated
    asyncio.run(run())


def test_absent_work_order_keeps_explicit_operational_gaps(history_graph):
    async def run():
        async with fixture_broker(history_graph) as b:
            r=await b.call('civicly::get_work_order_status',{'work_order_id':'WO-ABSENT','as_of':AS_OF})
            save('work_order-absent',r,history_graph)
            assert r['status']=='UNAVAILABLE' and r['error']['code']=='DATA_UNAVAILABLE'
            assert 'not verified empty' in ' '.join(r['data']['gaps'])
    asyncio.run(run())
