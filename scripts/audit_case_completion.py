"""Read-only audit of retained presenter cases before operator-assisted completion."""
import json
from pathlib import Path
from app.config import Settings
from app.graph.connection import connect
from app.graph.repository import GraphRepository
from app.active import load,active_scope
from app.graph.models import digest
from app.agents.checkpoints import saver
from app.services.evidence.writer import stable
from app.demo_host.config import load as host_load
from app.services.evidence.service import EvidenceService
from app.services.evidence.models import Journal

ROOT=Path('.runtime/demo-presenter/run-01')
CASES=['INV-B09-8b006fb97aa2b908fc69addcf7ecd037','INV-B09-917765cbf8fef632bd0459640c64f26f','INV-B09-95e00a75e74b708c966db68bc595dca0','INV-B09-9d231c8718136a90974e19c6c9a77c47','INV-B09-a2fe3dbdecd03984033026c4d0856295','INV-B09-b9d4d66e130ed348c4f6a50e9d66a891','INV-B09-f663f7a1473c4a28a941d147633e08ad']
def audit():
 config=host_load(ROOT/'host.json');profile=load(config.profile)
 with connect(Settings(_env_file='.env')) as db,active_scope(profile):
  repo=GraphRepository(db,profile.graph);cp=saver(profile);rows=[]
  for id in CASES:
   inv=repo.get_node(id,'Investigation');thread=inv.properties.get('thread_id');saved=cp.get_tuple({'configurable':{'thread_id':thread}}) if thread else None
   state=saved.checkpoint['channel_values']['data'] if saved else None
   key='civicly:b10:'+profile.graph+':'+digest(thread) if thread else None
   quarantine=db.connection.get(key+':quarantine') if key else None
   decisions=[]
   persisted=repo._read('MATCH (d:AgentDecision) WHERE d.rationale CONTAINS $thread RETURN d.id ORDER BY d.id LIMIT 101',{'thread':thread}) if thread else []
   if len(persisted)>100:raise RuntimeError('DECISION_AUDIT_BOUND')
   ids=sorted(set((state or {}).get('decisions',[]))|{r[0] for r in persisted})
   for did in ids:
    d=repo.get_node(did,'AgentDecision');v=json.loads(d.properties['rationale']);jid=did.replace('DEC-B10-','EV-B10-',1);journal=repo._node_optional(jid)
    if (v['metadata']['investigation_id'],v['metadata']['thread_id'])!=(id,thread):raise RuntimeError('AUDIT_DECISION_SCOPE')
    j=json.loads(journal.properties['summary']) if journal else None
    domain_id=stable('EV-JOURNAL','civicly-b10-analyst',jid);domain=repo._node_optional(domain_id)
    dv=json.loads(domain.properties['summary']) if domain else None
    receipt_checked=False
    if domain and dv.get('state')=='COMMITTED':
     record=Journal.model_validate_json(domain.properties['summary']);EvidenceService(repo).load(domain_id,record.request_hash);receipt=EvidenceService(repo).readback(record.receipt)
     if not j or j.get('status')!='COMMITTED' or receipt.model_dump(mode='json')!=j['result']:raise RuntimeError('DOMAIN_AND_DISPATCH_RECEIPT_MISMATCH')
     receipt_checked=True
    decisions.append({'decision_id':did,'in_checkpoint':did in (state or {}).get('decisions',[]),'decision_hash':d.content_hash,'action':v['selection']['action'],'tool':v['selection']['tool_name'],'dispatch_journal_id':jid,'dispatch_hash':journal.content_hash if journal else None,'dispatch_status':j.get('status') if j else None,'command_persisted':bool(j and j.get('command')),'domain_journal_id':domain_id,'domain_hash':domain.content_hash if domain else None,'domain_state':dv.get('state') if dv else None,'domain_receipt_readback_validated':receipt_checked})
   rows.append({'id':id,'native_status':inv.properties['status'],'native_hash':inv.content_hash,'thread_id':thread,'checkpoint_id':saved.config['configurable']['checkpoint_id'] if saved else None,'checkpoint_data_hash':digest(state) if state else None,'quarantine_hash':digest(quarantine.decode() if isinstance(quarantine,bytes) else quarantine) if quarantine else None,'lease_present':bool(key and db.connection.exists(key)),'pause':(state or {}).get('pause_reason'),'errors':(state or {}).get('errors',[]),'last_decisions':decisions})
  import sqlite3
  from app.agents.spending import DEFAULT_LEDGER
  with sqlite3.connect(DEFAULT_LEDGER.resolve().as_uri()+'?mode=ro',uri=True) as ledger:
   provider={'sessions':ledger.execute('SELECT count(*) FROM sessions').fetchone()[0],'open_holds':ledger.execute("SELECT count(*) FROM request_holds WHERE status='OPEN'").fetchone()[0],'unsettled_requests':ledger.execute('SELECT count(*) FROM requests WHERE charged IS NULL').fetchone()[0],'total_requests':ledger.execute('SELECT count(*) FROM requests').fetchone()[0]}
  return {'source_graph':profile.graph,'repository':repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.state,coalesce(m.repo_pending,''),m.repo_revision LIMIT 2"),'provider_accounting_readback':provider,'mode':'READ_ONLY_NO_RECONCILIATION_OR_REPLAY','cases':rows}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output)
 if out.exists():raise RuntimeError('AUDIT_OUTPUT_EXISTS')
 result=audit();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'output':str(out),'cases':len(result['cases']),'quarantines':sum(bool(c['quarantine_hash']) for c in result['cases']),'repository':result['repository']}))
