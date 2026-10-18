"""Sanitized retained B10 source/checkpoint witness using public SDK APIs only."""
import argparse,json,hashlib
from pathlib import Path
from app.active import load,active_scope,provision
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.graph.analysis.counterfactual import capture
from app.agents.checkpoints import saver
from app.mcp.civicly.runtime import configure


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--compare');parser.add_argument('--reprovision',action='store_true');args=parser.parse_args()
    p=load();fixture=json.loads(Path('docs/evidence/B10-live-fixture.json').read_text())
    with connect(Settings(_env_file='.env')) as db,active_scope(p):
        if args.reprovision:configure(db);provision(db,p)
        repo=GraphRepository(db,p.graph,lease_seconds=30);source=capture(repo).fingerprint
        sdk=saver(p);threads={}
        for case in [*fixture['cases'].values(),*fixture.get('previous_attempts',[])]:
            if not case.get('thread'):continue
            value=sdk.get_tuple({'configurable':{'thread_id':case['thread']}})
            assert value is not None,'Retained checkpoint missing'
            state=value.checkpoint['channel_values'].get('data',{})
            assert state['investigation_id']==case['investigation'] and state['graph']==p.graph
            threads[case['thread']]={'investigation_id':case['investigation'],'checkpoint_id':value.config['configurable']['checkpoint_id'],
                'public_state_sha256':hashlib.sha256(json.dumps(state,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                'decision_ids':state.get('decisions',[]),'execution_ids':state.get('executions',[]),'pause_reason':state.get('pause_reason')}
        # Stable accepted B09-R history checks do not depend on its rolling test file.
        # Native receipt-replay tests advance only writer lease metadata, not content/audit.
        old=json.loads(Path('docs/evidence/B09R-v1-proof.json').read_text())
        baseline=json.loads(Path('docs/evidence/B10-baseline-B09R-history.json').read_text())
        legacy_repo=GraphRepository(db,old['graph']);legacy_fp=capture(legacy_repo).fingerprint
        for key in ['graph','graph_revision','content_hash','audit_hash','audit_entries','nodes','edges']:
            assert legacy_fp[key]==baseline['fingerprint'][key],'Accepted B09-R history changed: '+key
        from app.services.evidence import EvidenceService
        from app.graph.schema import timestamp
        from datetime import timedelta
        at=(timestamp(old['correction_as_of'])+timedelta(seconds=100)).isoformat().replace('+00:00','Z')
        history=EvidenceService(legacy_repo).history(old['hypothesis_id'],at)
        assert [a.model_dump(mode='json') for a in history]==baseline['history'],'Assessment history changed'
        assert legacy_repo.get_node(old['v1_receipt']['entity_id']).content_hash==old['v1_assessment_node_hash']
        assert legacy_repo.get_node(old['v1_receipt']['journal_id']).content_hash==old['v1_journal_node_hash']
        accepted_history={'graph':old['graph'],'content_and_audit_unchanged':True,'assessment_versions_exact':True,
            'writer_lease_metadata_changed_by_native_replay_tests':legacy_fp['writer_state_hash']!=baseline['fingerprint']['writer_state_hash']}
        counts=db.select_graph(p.checkpoints).ro_query('MATCH (n) RETURN labels(n),count(n) ORDER BY labels(n)').result_set
        from app.mcp.civicly.runtime import connections
        from app.mcp.civicly.storage import TraceStore
        with connections() as (_,writer,name):
            store=TraceStore(writer,name)
            for t in threads.values():
                for id in t['execution_ids']:assert store.get(id) is not None,'Durable execution missing'
        hashes={str(name):hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in ['contracts/schema_registry.json','backend/app/graph/migrations/0001.json','backend/app/graph/migrations/0002_mcp_traces.json'] if Path(name).exists()}
        value={'status':'PASS','source':source,'checkpoint_graph':p.checkpoints,'checkpoint_counts':counts,'threads':threads,'immutable_source_hashes':hashes,'secrets_logged':False,'accepted_B09R_history':accepted_history}
        if args.compare:
            old=json.loads(Path(args.compare).read_text())
            for key in ['source','checkpoint_graph','checkpoint_counts','threads','immutable_source_hashes']:assert value[key]==old[key],'Retained B10 changed: '+key
            value['matches_before_lifecycle']=True
        Path(args.output).write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':'PASS','threads_verified':len(threads),'matches_before_lifecycle':bool(args.compare)}))
if __name__=='__main__':main()
