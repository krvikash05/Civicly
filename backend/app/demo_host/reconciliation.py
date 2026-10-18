"""Explicit operator no-effect attestation for one undispatched historical PROPOSE."""
import json
from pathlib import Path
from app.agents.checkpoints import saver
from app.graph.models import digest
from app.graph.schema import utc_now
from app.services.evidence.writer import stable
from app.services.operations.auth import Auth
from app.services.operations.storage import Storage
from app.events.service import Delivery
from cli.private import read_json
from .runtime import HostBlocked


def no_effect(repo,case,decision_id):
    if not decision_id.startswith('DEC-B10-'):raise HostBlocked('RECONCILIATION_DECISION_ID')
    decision=repo.get_node(decision_id,'AgentDecision');value=json.loads(decision.properties['rationale'])
    meta=value['metadata']
    if (meta.get('investigation_id'),meta.get('thread_id'))!=(case.investigation_id,case.thread_id) or value['selection']['action']!='PROPOSE':raise HostBlocked('RECONCILIATION_DECISION_SCOPE')
    request=decision_id.replace('DEC-B10-','EV-B10-',1)
    journal=stable('EV-JOURNAL','civicly-b10-analyst',request);entity=stable('HYP',journal)
    absent=[request,journal,entity]
    if any(repo._node_optional(id) is not None for id in absent):raise HostBlocked('RECONCILIATION_DISPATCH_OR_EFFECT_EXISTS')
    rows=repo._read("MATCH (m:CivicSchemaMigration {id:'0001'}) RETURN m.state,coalesce(m.repo_pending,''),m.repo_revision LIMIT 2")
    if len(rows)!=1 or rows[0][0]!='READY' or rows[0][1]:raise HostBlocked('RECONCILIATION_REPOSITORY_UNCERTAIN')
    return {'decision_id':decision_id,'decision_hash':decision.content_hash,'request_id':request,
        'domain_journal_id':journal,'hypothesis_id':entity,'absent_ids':absent,'source_revision':rows[0][2],
        'conclusion':'NO_DISPATCH_JOURNAL_OR_DOMAIN_EFFECT','dispatch_rule':'B10 must persist its dispatch journal and original command before calling B09; B09 hypothesis and journal commit atomically'}


def valid_reconciliation(config,profile,repo,case,state):
    row=Storage(repo).get('demo_reconciliation',case.thread_id)
    if row is None:return False
    if row.get('version')!=1 or row.get('authorized_by_human') is not True or row.get('original_checkpoint_or_error_modified') is not False or row.get('quarantine_cleared') is not False or row.get('original_operation_replayed') is not False:raise HostBlocked('RECONCILIATION_ATTESTATION_INVALID')
    if row['source_graph']!=profile.graph or row['investigation_id']!=case.investigation_id or row['thread_id']!=case.thread_id or row['actor']['role']!='ADMIN':raise HostBlocked('RECONCILIATION_ATTESTATION_SCOPE')
    if state.errors.count('WRITE_OUTCOME_UNKNOWN')!=row['unknown_error_count']:raise HostBlocked('RECONCILIATION_NEW_UNCERTAINTY')
    old=saver(profile).get_tuple({'configurable':{'thread_id':case.thread_id,'checkpoint_id':row['checkpoint_id']}})
    if old is None or digest(old.checkpoint['channel_values']['data'])!=row['checkpoint_sha256']:raise HostBlocked('RECONCILIATION_ORIGINAL_CHECKPOINT_CHANGED')
    current=no_effect(repo,case,row['proof']['decision_id'])
    if any(current[k]!=row['proof'][k] for k in ['decision_hash','request_id','domain_journal_id','hypothesis_id','absent_ids']):raise HostBlocked('RECONCILIATION_PROOF_CHANGED')
    return True


def reconcile(config,profile,repo,case_id,decision_id,*,authorized=False):
    if authorized is not True:raise HostBlocked('EXPLICIT_RECONCILIATION_AUTHORIZATION_REQUIRED')
    case=next((c for c in config.cases if c.investigation_id==case_id),None)
    if case is None:raise HostBlocked('CASE_NOT_HOST_AUTHORIZED')
    auth=Auth(config.auth_store);passwords=read_json(Path(config.auth_store).parent/'presenter-credentials.json',private=True)
    token=auth.login('OP-ADMIN',passwords['OP-ADMIN'])
    try:
        actor=auth.resolve(token)
        if actor.role!='ADMIN':raise HostBlocked('RECONCILIATION_ADMIN_REQUIRED')
        from .source import source_writer
        with source_writer(repo):
            key='civicly:b10:'+profile.graph+':'+digest(case.thread_id)
            if repo.client.connection.exists(key,key+':quarantine'):raise HostBlocked('RECONCILIATION_LEASE_OR_QUARANTINE_PRESENT')
            saved=saver(profile).get_tuple({'configurable':{'thread_id':case.thread_id}})
            if saved is None:raise HostBlocked('RECONCILIATION_CHECKPOINT_MISSING')
            state=saved.checkpoint['channel_values']['data']
            if state['errors'].count('WRITE_OUTCOME_UNKNOWN')!=1 or decision_id not in state['decisions'] or state['pause_reason']!='MISSING_EVIDENCE':raise HostBlocked('RECONCILIATION_NOT_SUPPORTED')
            proof=no_effect(repo,case,decision_id)
            row={'version':1,'source_graph':profile.graph,'investigation_id':case_id,'thread_id':case.thread_id,
                'checkpoint_id':saved.config['configurable']['checkpoint_id'],'checkpoint_sha256':digest(state),
                'unknown_error_count':1,'proof':proof,'actor':actor.model_dump(mode='json'),'authorized_by_human':True,
                'at':utc_now(),'original_checkpoint_or_error_modified':False,'quarantine_cleared':False,
                'original_operation_replayed':False,'reason':'Explicit human-authorized original incident review; absent mandatory dispatch/domain journals and native effect prove no analytical write'}
            store=Delivery(repo,utc_now).store
            if store.get('demo_reconciliation',case.thread_id):raise HostBlocked('RECONCILIATION_ALREADY_RECORDED')
            with repo._session() as session:store.write(session,[('demo_reconciliation',case.thread_id,row)])
            if store.get('demo_reconciliation',case.thread_id)!=row:raise HostBlocked('RECONCILIATION_READBACK_FAILED')
            return row
    finally:auth.logout(token)
