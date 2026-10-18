"""B08 trusted domain intake, transparent grouping and explicit reviewed correction."""
from app.active import is_shared_target
import json
from datetime import timedelta
from app.graph.models import EdgeRecord,PathRecord,digest
from app.graph.queries import GraphQueries
from app.graph.repository import Conflict,PreconditionFailed,intersection,interval
from app.graph.schema import utc_now,timestamp
from .models import normalize,INTAKE,Journal,IntakeResult,Review,utc,EvidenceRef
from .reader import Reader
from .writer import Writer,node


def stable(prefix,*parts):return prefix+'-'+digest(parts)[:32]
def common(id,now):return {'id':id,'schema_version':3,'municipality_id':'demo-city','created_at':now,'updated_at':now}
def link(kind,s,t,journal,now):
    return EdgeRecord(id=stable('REL-B08',kind,s,t,journal),kind=kind,source=s,target=t,
        properties={'id':stable('REL-B08',kind,s,t,journal),'municipality_id':'demo-city','created_at':now,'valid_from':now,'source_evidence_id':journal,**({'association_status':'REPORTED'} if kind=='AFFECTS' else {})})

def same_event(q,c):
    n=c['node'];p=n.properties
    if not q.asset_ids and not q.event_reference:return False
    if p['status'] not in {'REPORTED','ACTIVE','MITIGATED'}:return False
    if p['issue_type']!=q.issue_type or p['subtype']!=q.subtype or c['locations']!={q.location_id} or c['assets']!=set(q.asset_ids):return False
    if q.event_reference:
        if c['events']!={(q.source_id,q.event_reference)}:return False
    elif c['events']:return False
    if intersection((timestamp(q.occurred_at),timestamp(q.ended_at) if q.ended_at else None),
                    (timestamp(p['started_at']),timestamp(p['ended_at']) if p.get('ended_at') else None)) is None:return False
    return bool(q.event_reference) or abs(timestamp(q.occurred_at)-timestamp(p['started_at']))<=timedelta(hours=24)


def pattern(members,q):
    if len({n.properties['issue_type'] for n in members})>1:return 'CROSS_CATEGORY','RELATED_CROSS_CATEGORY'
    ended=[n for n in members if n.properties['status']=='ENDED' and n.properties.get('ended_at') and timestamp(n.properties['ended_at'])<timestamp(q.occurred_at)]
    if ended:return 'RECURRENT','AFTER_RECORDED_END'
    if len(members)>1 or timestamp(q.reported_at)-timestamp(q.occurred_at)>=timedelta(hours=24):return 'PERSISTENT','CONTINUING_UNRESOLVED'
    return 'SINGLE_EVENT','NEW_OCCURRENCE'

class ComplaintService:
    def __init__(self,repository,*,clock=utc_now):self.repo=repository;self.clock=clock
    def write_target(self):
        name=self.repo.graph.name
        if name!='civicly_knowledge' and not name.startswith('civicly_b08_test_') and not is_shared_target(name):raise PreconditionFailed('B08 writes restricted to canonical or isolated B08 graph; retained sources read-only')
    def load(self,id,request_hash,operation='INTAKE'):
        n=self.repo._node_optional(id)
        if n is None:return None,None
        expected='COMPLAINT_INTAKE' if operation=='INTAKE' else 'GROUPING_CORRECTION'
        if n.kind!='Evidence' or n.properties['evidence_type']!=expected or n.properties['reliability']!='UNVERIFIED':raise Conflict('Reserved journal identity collision/invalid reliability')
        j=Journal.model_validate_json(n.properties['summary'])
        if j.operation!=operation or j.request_hash!=request_hash or digest(j.canonical)!=j.request_hash:raise Conflict('External source ID/request reused with different content/version')
        return n,j
    def prepare(self,id,original,canonical,request_hash,now,source_kind,source_record,operation='INTAKE'):
        n,j=self.load(id,request_hash,operation)
        if n:return n,j
        j=Journal(operation=operation,original=original,canonical=canonical,request_hash=request_hash)
        try:
            n=self.repo.create_node('Evidence',{**common(id,now),'evidence_type':'COMPLAINT_INTAKE' if operation=='INTAKE' else 'GROUPING_CORRECTION',
                'summary':j.serialized(),'reliability':'UNVERIFIED','recorded_at':now,'source_kind':source_kind,'source_record_id':source_record})
            return n,j
        except Conflict:return self.load(id,request_hash,operation) # concurrent exact prepare; no uncertain-write retry
    def receipt(self,journal,replayed=False):
        r=IntakeResult.model_validate_json(json.dumps(journal.receipt))
        # A durable historical receipt is not a reconstruction of present memberships.
        if {ref.id for ref in r.evidence_references}!=set(r.source_evidence_ids):raise PreconditionFailed('Persisted receipt evidence references mismatch')
        for path in r.graph_paths:
            supported={id for id in path.node_ids if self.repo.get_node(id).kind=='Evidence'}
            for i,id in enumerate(path.edge_ids):
                e=self.repo.get_relationship(id)
                ends=(e.source,e.target) if path.directions[i]=='OUTGOING' else (e.target,e.source)
                if ends!=(path.node_ids[i],path.node_ids[i+1]):raise PreconditionFailed('Persisted receipt relationship mismatch')
                if e.properties.get('source_evidence_id'):supported.add(e.properties['source_evidence_id'])
            if not set(path.evidence_ids)<=supported or not set(path.evidence_ids)<=set(r.source_evidence_ids):raise PreconditionFailed('Persisted receipt path evidence mismatch')
        for id in r.source_evidence_ids:self.repo.get_node(id,'Evidence')
        if replayed:return r.model_copy(update={'replayed':True,'historical_receipt':True,'uncertainty':[*r.uncertainty,'Historical intake receipt; later reviewed grouping changes require a current graph read.']})
        return r
    def preview(self,payload):
        q,norm=normalize(payload);now=utc(self.clock())
        if timestamp(q.reported_at)>timestamp(now):raise PreconditionFailed('Report after service clock')
        before=GraphQueries(self.repo)._state();result,*_=self.plan(q,norm,now,before,preview=True)
        if GraphQueries(self.repo)._state()!=before:raise PreconditionFailed('Source changed during preview')
        return result
    def intake(self,payload):
        self.write_target();q,norm=normalize(payload);now=utc(self.clock())
        if timestamp(q.reported_at)>timestamp(now):raise PreconditionFailed('Report after service clock')
        jid=stable('EV-B08',q.source_kind,q.source_id,q.external_record_id)
        # Invalid missing references cannot create an orphan intake journal.
        Reader(self.repo,now).references(q)
        self.prepare(jid,norm.original,norm.canonical,norm.request_hash,now,q.source_kind,q.source_id+':'+q.external_record_id)
        with self.repo._session() as session:
            journal,j=self.load(jid,norm.request_hash)
            if j.state=='COMMITTED':return self.receipt(j,True)
            q,norm=normalize(j.original)
            if norm.request_hash!=j.request_hash:raise Conflict('Stored original/canonical request mismatch')
            now=utc(self.clock());result,new,updates,edges=self.plan(q,norm,now,session.revision+1)
            committed=j.model_copy(update={'state':'COMMITTED','receipt':result.model_dump(mode='json')})
            Writer(self.repo).commit(session,journal,new,updates,edges,[],committed.serialized(),now)
        _,actual=self.load(jid,norm.request_hash)
        if actual.state!='COMMITTED':raise PreconditionFailed('Intake commit did not persist receipt')
        return self.receipt(actual)
    def plan(self,q,norm,now,revision,preview=False,*,planned_journal=None):
        reader=Reader(self.repo,now);reader.references(q);contexts=reader.candidates(q);assessment=reader.assessment(q)
        same=[c for c in contexts.values() if same_event(q,c)]
        uncertainty=['Reported associations and grouping are context, not verified causes or resolution.',
            'Search limited to100 incidents/400 context edges/200 report journals,4 infrastructure hops; no global-absence claim.',
            'Historical node versions are not reconstructed; future-updated records excluded.']
        if len(same)>1:uncertainty.append('Multiple compatible ongoing incidents; no arbitrary event merge.');same=[]
        related=[]
        topology_pairs={(p.node_ids[0],p.node_ids[-1]) for p in reader.topology}
        for c in contexts.values():
            p=c['node'].properties
            if p['status']=='INVALIDATED':continue
            if p['status']=='ENDED' and not p.get('ended_at'):
                uncertainty.append('Ended incident '+c['node'].id+' lacks termination date; recurrence indeterminate.');continue
            exact=bool(q.asset_ids) and c['assets']==set(q.asset_ids) and c['locations']=={q.location_id} and p['issue_type']==q.issue_type and p['subtype']==q.subtype
            cross=p['issue_type']!=q.issue_type and (bool(set(q.asset_ids)&c['assets']) or any((a,b) in topology_pairs or (b,a) in topology_pairs for a in q.asset_ids for b in c['assets']))
            if exact or cross:related.append(c)
        cid=stable('CMP-B08',q.source_kind,q.source_id,q.external_record_id);jid=stable('EV-B08',q.source_kind,q.source_id,q.external_record_id)
        incident=same[0]['node'] if same else node(self.repo,'Incident',{**common(stable('INC-B08',cid),now),
            'issue_type':q.issue_type,'subtype':q.subtype,'severity':q.severity,'status':'REPORTED','started_at':q.occurred_at,
            **({'ended_at':q.ended_at} if q.ended_at else {})})
        cluster_ids=set(same[0]['clusters']) if same else {id for c in related for id in c['clusters']}
        clusters=[reader.node(id,'ProblemCluster') for id in sorted(cluster_ids)]
        clusters=[n for n in clusters if n.properties['status']!='ARCHIVED']
        if len(clusters)>1:uncertainty.append('Multiple eligible primary clusters '+','.join(n.id for n in clusters)+'; separate cluster proposed for review.');clusters=[]
        if same and len(same[0]['clusters'])>1:raise PreconditionFailed('Existing incident has conflicting primary assignments')
        if same and same[0]['clusters'] and not clusters:raise PreconditionFailed('Existing primary cluster unavailable; review before intake')
        members=reader.members(clusters[0].id) if clusters else []
        if incident.id not in {n.id for n in members}:members.append(incident)
        kind,classification=pattern(members,q)
        if same:classification='SAME_INCIDENT'
        if kind=='PERSISTENT':uncertainty.append('Persistence is provisional reported context; missing termination/outcome verification cannot rule out unrecorded resolution.')
        cluster=clusters[0] if clusters else node(self.repo,'ProblemCluster',{**common(stable('PC-B08',incident.id),now),
            'title':q.issue_type+' reported at '+q.location_id,'status':'OPEN','first_seen_at':min((n.properties['started_at'] for n in members),key=timestamp),'pattern_type':kind})
        updates=[]
        if clusters:
            cluster=node(self.repo,'ProblemCluster',{**cluster.properties,'pattern_type':kind,'updated_at':now,
                'first_seen_at':min([cluster.properties['first_seen_at'],*[n.properties['started_at'] for n in members]],key=timestamp)})
            updates=[cluster]
        complaint=node(self.repo,'Complaint',{**common(cid,now),'description':q.description,'reported_at':q.reported_at,
            'source_channel':q.source_channel,'source_kind':q.source_kind,'source_id':q.source_id,'external_record_id':q.external_record_id,
            'source_version':q.source_version,'status':'RECEIVED'})
        new=[complaint]+([] if same else [incident])+([] if clusters else [cluster])
        edges=[link('REPORTS',cid,incident.id,jid,now)]
        if not same:
            edges+=[link('OCCURRED_AT',incident.id,q.location_id,jid,now)]
            edges+=[link('AFFECTS',incident.id,id,jid,now) for id in q.asset_ids]
        if not same or not same[0]['clusters']:edges.append(link('PART_OF',incident.id,cluster.id,jid,now))
        paths=[]
        for e in edges:
            paths.append(PathRecord(node_ids=(e.source,e.target),edge_ids=(e.id,),directions=('OUTGOING',),evidence_ids=(jid,),context={'classification':'REPORTED_INTAKE_CONTEXT'}))
        membership=next((e for e in edges if e.kind=='PART_OF'),None)
        if membership is None and same:membership=next(e for e in same[0]['edges'] if e.kind=='PART_OF' and e.target==cluster.id)
        chain_evidence=tuple(sorted({jid}|({membership.properties['source_evidence_id']} if membership.properties.get('source_evidence_id') else set())))
        paths.append(PathRecord(node_ids=(cid,incident.id,cluster.id),edge_ids=(edges[0].id,membership.id),directions=('OUTGOING','OUTGOING'),evidence_ids=chain_evidence,context={'classification':'COMPLAINT_INCIDENT_PRIMARY_CLUSTER'}))
        for c in related:
            for e in c['edges']:
                reader.paths.append(PathRecord(node_ids=(e.source,e.target),edge_ids=(e.id,),directions=('OUTGOING',),evidence_ids=(e.properties['source_evidence_id'],) if e.properties.get('source_evidence_id') else (),context={'classification':'RECORDED_PRIOR_CONTEXT'}))
        if len(reader.paths)>90:uncertainty.append('Supporting proof export capped; omitted context is not absence.')
        unique_paths={digest(p.model_dump(mode='json')):p for p in reader.paths}
        context_paths=list(unique_paths.values())[:90]
        source_ids=set(assessment.source_evidence_ids)|{id for p in context_paths for id in p.evidence_ids}|(set(chain_evidence) if not preview else set())
        references=[]
        if planned_journal is not None:
            self.repo.registry.validate_node('Evidence',planned_journal)
            expected=Journal(operation='INTAKE',original=norm.original,canonical=norm.canonical,request_hash=norm.request_hash)
            if planned_journal['id']!=jid or planned_journal['evidence_type']!='COMPLAINT_INTAKE' or planned_journal['summary']!=expected.serialized() or planned_journal['reliability']!='UNVERIFIED' or planned_journal['source_kind']!=q.source_kind or planned_journal['source_record_id']!=q.source_id+':'+q.external_record_id or planned_journal['recorded_at']!=now:raise PreconditionFailed('Planned intake journal binding mismatch')
        for id in sorted(source_ids):
            ev=planned_journal if id==jid and planned_journal is not None else reader.node(id,'Evidence').properties
            references.append(EvidenceRef(id=id,recorded_at=ev['recorded_at'],observed_at=ev.get('observed_at'),source_kind=ev['source_kind'],reliability=ev['reliability']))
        explanations=['Same-event start gap is at most24 hours unless source+event reference matches; declared intervals must overlap.',
            'Matched by explicit issue/subtype/location/assets and occurrence intervals, never report count or spatial proximity.',
            'Incident status remains REPORTED; claimed end does not establish verified resolution.',
            'RECURRENT requires a distinct occurrence after a recorded ENDED interval; completed orders alone do not qualify.']
        if kind=='CROSS_CATEGORY':explanations.append('Different issue categories remain distinct incidents; shared reported asset or verified dependency provides contextual grouping only.')
        for c in related[:20]:
            p=c['node'].properties
            explanations.append('Related '+c['node'].id+': issue='+p['issue_type']+', status='+p['status']+', started_at='+p['started_at']+', ended_at='+p.get('ended_at','unknown')+', explicit_assets='+','.join(sorted(c['assets']))+', primary_clusters='+','.join(sorted(c['clusters']))+'.')
        if len(related)>20:uncertainty.append('Detailed matching explanations capped at20 related incidents.')
        projected=[]
        for p in [*context_paths,*([] if preview else paths)]:
            projected.append(p.model_copy(update={'context':{**p.context,'path_id':getattr(p,'id',stable('PATH-B08',p.node_ids,p.edge_ids,p.directions))}}))
        uncertainty.extend(assessment.gaps)
        return (IntakeResult(graph=self.repo.graph.name,complaint_id=cid,incident_id=incident.id,cluster_id=cluster.id,journal_id=jid,pattern_type=kind,
            classification=classification,created_incident=not bool(same),related_incident_ids=sorted({c['node'].id for c in related}),
            matched_attributes=['issue_type='+q.issue_type,'subtype='+q.subtype,'location_id='+q.location_id,'explicit_assets='+','.join(q.asset_ids),'occurred_at='+q.occurred_at,'ended_at='+(q.ended_at or 'unknown'),'source_event_reference='+((q.source_id+':'+q.event_reference) if q.event_reference else 'absent')],
            explanations=explanations,uncertainty=list(dict.fromkeys(uncertainty)),assessment=assessment,
            graph_paths=projected,source_evidence_ids=sorted(source_ids|({jid} if not preview else set())),
            evidence_references=references,graph_revision=revision,as_of=now,truncated=len(reader.paths)>90 or len(related)>20,preview=preview),new,updates,edges)
    def incomplete(self):
        rows=self.repo._read("MATCH (e:Evidence) WHERE e.evidence_type IN $types RETURN e.id,e.summary LIMIT 101",{'types':['COMPLAINT_INTAKE','GROUPING_CORRECTION']})
        if len(rows)>100:raise PreconditionFailed('Intake reconciliation budget exceeded')
        return [id for id,summary in rows if Journal.model_validate_json(summary).state=='PREPARED']
    def regroup(self,review):
        self.write_target()
        if not isinstance(review,Review):raise TypeError('Trusted typed reviewer context required')
        now=utc(self.clock());canonical=review.model_dump(mode='json');sha=digest(canonical);jid=stable('EV-REGROUP-B08',review.reviewer_id,review.request_id)
        self.prepare(jid,canonical,canonical,sha,now,'USER',review.reviewer_id+':'+review.request_id,'REGROUP')
        with self.repo._session() as session:
            journal,j=self.load(jid,sha,'REGROUP')
            if j.state=='COMMITTED':return {**j.receipt,'replayed':True}
            reader=Reader(self.repo,now);incident=reader.node(review.incident_id,'Incident');target=reader.node(review.target_cluster_id,'ProblemCluster')
            rows=self.repo._edges('PART_OF');active=[e for e in rows if e.source==incident.id and visible_edge(e,now)]
            if len(active)!=1:raise PreconditionFailed('Exactly one active primary membership required')
            old=active[0]
            if incident.content_hash!=review.expected_incident_hash or old.content_hash!=review.expected_membership_hash or target.content_hash!=review.expected_target_hash:raise PreconditionFailed('Stale grouping review')
            if old.target==target.id or target.properties['status']=='ARCHIVED':raise PreconditionFailed('Correction target must be a different active cluster')
            if not old.properties.get('valid_from') or timestamp(old.properties['valid_from'])>=timestamp(now):raise PreconditionFailed('Known nonempty old membership interval required')
            closed=old.model_copy(update={'properties':{**old.properties,'valid_to':now}})
            replacement=link('PART_OF',incident.id,target.id,jid,now)
            # Recalculate category pattern; unresolved/ended ambiguity remains explicit.
            updates=[]
            for id in [old.target,target.id]:
                cluster=reader.node(id,'ProblemCluster');members=[n for n in reader.members(id) if n.id!=incident.id]
                if id==target.id:members.append(incident)
                categories={n.properties['issue_type'] for n in members}
                kind='CROSS_CATEGORY' if len(categories)>1 else 'PERSISTENT' if len(members)>1 else 'SINGLE_EVENT'
                if len(categories)==1 and any(a.properties['status']=='ENDED' and a.properties.get('ended_at') and timestamp(a.properties['ended_at'])<timestamp(b.properties['started_at']) for a in members for b in members if a.id!=b.id):kind='RECURRENT'
                updates.append(node(self.repo,'ProblemCluster',{**cluster.properties,'pattern_type':kind,'updated_at':now}))
            receipt={'journal_id':jid,'incident_id':incident.id,'old_cluster_id':old.target,'cluster_id':target.id,
                     'old_membership_id':old.id,'membership_id':replacement.id,'effective_at':now,'reviewer_id':review.reviewer_id,
                     'reason':review.reason,'graph_revision':session.revision+1,'replayed':False,
                     'limitations':['Reviewed grouping correction, not causal verification or operational resolution.']}
            committed=j.model_copy(update={'state':'COMMITTED','receipt':receipt})
            Writer(self.repo).commit(session,journal,[],updates,[replacement],[closed],committed.serialized(),now)
        _,actual=self.load(jid,sha,'REGROUP');return actual.receipt

def visible_edge(edge,now):
    start,end=interval(edge.properties);at=timestamp(now)
    return (start is None or start<=at) and (end is None or at<end)
