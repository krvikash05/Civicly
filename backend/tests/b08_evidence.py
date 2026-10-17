"""Operator-only synthetic B08 fixture proof. No city import or graph deletion."""
import argparse,json
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.migration import MigrationRunner
from app.graph.repository import GraphRepository
from app.graph.targets import new_test_graph_name
from app.graph.analysis.counterfactual import capture
from app.services.complaints import ComplaintService
from tests.b08_fixtures import populate,payload,CLOCK
from tests.schema_examples import edge


def run():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['create','verify']);parser.add_argument('--proof',type=Path,required=True);parser.add_argument('--output',type=Path);parser.add_argument('--anchor',type=Path);parser.add_argument('--lifecycle-log',type=Path)
    args=parser.parse_args()
    with connect(Settings(_env_file='.env')) as db:
        if args.action=='create':
            if args.proof.exists():raise ValueError('Refuse to overwrite retained proof; verify it or choose a new path')
            name=new_test_graph_name(8);MigrationRunner(db,name).apply();repo=GraphRepository(db,name,lease_seconds=30);populate(repo)
            repo.create_relationship('UNDERLIES','P1','R1',{**edge('RETAINED-P-R'),'association_status':'VERIFIED','source_evidence_id':'EV'})
            before=capture(repo).fingerprint;s=ComplaintService(repo,clock=lambda:CLOCK)
            requests=[payload(ref='retained-a'),payload(ref='retained-b',source_id='independent-source'),payload(ref='retained-c',event_reference='independent-event'),payload('ROAD_DAMAGE',ref='retained-road'),payload(ref='retained-pipe',asset_ids=['P1'])]
            receipts=[s.intake(request).model_dump(mode='json') for request in requests]
            rows=repo._read('MATCH (c:Complaint)-[:REPORTS]->(i:Incident)-[:PART_OF]->(p:ProblemCluster) RETURN c.id,i.id,i.issue_type,p.id,p.pattern_type ORDER BY c.id')
            report={'status':'PASS','evidence_class':'REAL_FALKORDB_AUTHORED_SYNTHETIC_B08_FIXTURE','source_city_modified':False,'graph':name,'before':before,'after':capture(repo).fingerprint,'requests':requests,'receipts':receipts,'actual_chains':rows,'note':'Retained for human review and real lifecycle verification; no hidden scenario sources.'}
            args.proof.write_text(json.dumps(report,indent=2)+'\n')
        else:
            proof=json.loads(args.proof.read_text());repo=GraphRepository(db,proof['graph'],lease_seconds=30)
            fresh=capture(repo).fingerprint
            anchor=json.loads(args.anchor.read_text())['after_retry'] if args.anchor else proof['after']
            assert fresh==anchor
            if args.lifecycle_log:
                log=args.lifecycle_log.read_text();assert 'after restart (same container)' in log and 'after recreation (different container, retained volume)' in log and 'passed in' in log
            s=ComplaintService(repo,clock=lambda:CLOCK)
            for request,old in zip(proof['requests'],proof['receipts'],strict=True):
                replay=s.intake(request);assert replay.replayed and replay.complaint_id==old['complaint_id'] and replay.incident_id==old['incident_id'] and replay.cluster_id==old['cluster_id']
            after=capture(repo).fingerprint
            for key in ['content_hash','graph_revision','audit_hash','audit_entries','nodes','edges']:assert fresh[key]==after[key]
            report={'status':'PASS','graph':repo.graph.name,'fresh_before_retry':fresh,'after_retry':after,'all_journals_and_chains_preserved':True,'all5_retries_no_domain_changes':True,'lifecycle_log_verified':bool(args.lifecycle_log),'note':'Writer owner/epoch can change on replay; domain revision/audit/content do not. Lifecycle asserted only when actual successful log supplied.'}
            if not args.output:raise ValueError('Verification output required')
            args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':'PASS','action':args.action,'output':str(args.proof if args.action=='create' else args.output)}))

if __name__=='__main__':run()
