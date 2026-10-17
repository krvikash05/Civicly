import json
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.analysis.counterfactual import capture
from tests.b09_fixtures import create,open_case,propose,report,assess
from app.services.evidence.models import Journal
with connect(Settings(_env_file='.env')) as db:
 f=create(db,retain_source=True)
 inv=open_case(f);h=propose(f,inv)
 ev=report(f,inv,codes=['DRAIN_CLEAR'],reviewed=False).entity_id
 result=assess(f,h,[ev])
 journal=Journal.model_validate_json(f.repo.get_node(result.journal_id).properties['summary'])
 value={'graph':f.repo.graph.name,'source_graph':f.source_graph,'source_fingerprint':f.source_fingerprint,
        'investigation_id':inv,'hypothesis_id':h,'clock':f.clock(),'v1_receipt':result.model_dump(mode='json'),
        'v1_command':journal.command,'actor':journal.actor.model_dump(mode='json'),
        'v1_assessment_node_hash':f.repo.get_node(result.entity_id).content_hash,
        'v1_journal_node_hash':f.repo.get_node(result.journal_id).content_hash,'before':capture(f.repo).fingerprint}
 Path('/tmp/civicly-b09r-v1-proof.json').write_text(json.dumps(value,indent=2)+'\n')
 print(json.dumps({'status':'PASS','legacy_graph':f.repo.graph.name,'v1_label':result.assessment.assessment}))
