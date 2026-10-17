import json
from app.config import Settings
from app.graph.connection import connect
from tests.b09_fixtures import create,open_case,propose,report,assess
from tests.graph_fixtures import evidence

results={}
with connect(Settings(_env_file='.env')) as db:
 for case in ['unreviewed-contradiction','context-as-support','after-episode-end']:
  f=create(db)
  try:
   inv=open_case(f)
   h=propose(f,inv)
   if case=='unreviewed-contradiction':
    e=report(f,inv,codes=['DRAIN_CLEAR'],reviewed=False).entity_id
   elif case=='context-as-support':
    e=evidence(f.repo,'CONTEXT',evidence_type='LLM_STATEMENT',source_kind='AGENT').id
   else:
    incident=f.repo.get_node(f.receipts['WATERLOGGING'].incident_id)
    active=f.repo.update_node(incident.id,{'status':'ACTIVE'},expected_hash=incident.content_hash)
    f.repo.update_node(active.id,{'status':'ENDED','ended_at':'2026-10-18T11:00:00Z'},expected_hash=active.content_hash)
    e=report(f,inv).entity_id
   r=assess(f,h,[e]);a=r.assessment
   results[case]={'assessment':a.assessment,'persisted_assessment':f.repo.get_node(a.id).properties['assessment'],
    'hypothesis_status':f.repo.get_node(h).properties['status'],'supporting_evidence_ids':a.supporting_evidence_ids,
    'contradicting_evidence_ids':a.contradicting_evidence_ids,'supported_by':[v.target for v in f.repo._edges('SUPPORTED_BY') if v.source==a.id],
    'contradicted_by':[v.target for v in f.repo._edges('CONTRADICTED_BY') if v.source==a.id],'gaps':a.missing_evidence,
    'evidence_class':'REAL_FALKORDB_AUTHORED_ISOLATED_FIXTURE'}
  finally:db.select_graph(f.repo.graph.name).delete()
open('docs/evidence/B09R-after-results.json','w').write(json.dumps(results,indent=2)+'\n')
print(json.dumps({key:{'assessment':v['assessment'],'status':v['hypothesis_status']} for key,v in results.items()}))
