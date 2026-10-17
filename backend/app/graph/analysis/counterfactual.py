"""Owned B05 clones only. Original source has no mutation/cleanup path here."""
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import time
from app.graph.models import digest, GraphModel, EdgeRecord
from app.graph.repository import GraphRepository, PreconditionFailed, OutcomeUnknown
from app.graph.migration import MigrationRunner
from app.graph.schema import utc_now
from app.graph.targets import new_test_graph_name, is_disposable_graph
from app.ingestion.conversion import check_graph
from .models import AnalysisLimits, AnalysisRequest, AnalysisResult
from .reader import Reader, AnalysisBudgetExceeded
from .engine import GraphAnalysis


@dataclass
class Snapshot:
    nodes: list
    edges: list
    records: dict
    fingerprint: dict


def capture(repository, limits=None):
    """Administrative complete bounded clone export, including future/expired records."""
    limits=limits or AnalysisLimits()
    q=AnalysisRequest(operation='components',ids=('SNAPSHOT',),as_of=utc_now())
    meter={'queries':0,'steps':0,'started':time.perf_counter()}
    r=Reader(repository,q,limits,meter)
    for _ in range(2):
        before=r.state()
        ns=r.query('MATCH (n:CivicEntity) RETURN labels(n),properties(n) LIMIT $cap',{'cap':limits.max_nodes+1})
        es=r.query('MATCH (s:CivicEntity)-[e]->(t:CivicEntity) RETURN type(e),properties(e),labels(s),properties(s),labels(t),properties(t) LIMIT $cap',{'cap':limits.max_edges+1})
        if len(ns)>limits.max_nodes or len(es)>limits.max_edges:raise AnalysisBudgetExceeded('Complete clone source exceeds bounded node/edge export; select a reviewed small fixture')
        nodes=[repository.decode_node(*row) for row in ns];edges=[repository._decode_edge_row(row) for row in es]
        meta=r.query("MATCH (m:CivicSchemaMigration {id:$id}) RETURN coalesce(m.repo_revision,0),coalesce(m.repo_audit,'[]'),coalesce(m.repo_pending,''),coalesce(m.repo_epoch,0),coalesce(m.repo_owner,'') LIMIT 1",{'id':'0001'})[0]
        if meta[2]:raise PreconditionFailed('Source has pending write')
        if before!=meta[0] or r.state()!=before:continue
        records={n.id:n.content_hash for n in nodes};records.update({e.id:e.content_hash for e in edges})
        if len(records)!=len(nodes)+len(edges):raise PreconditionFailed('Duplicate snapshot identity')
        fp={'graph':repository.graph.name,'graph_revision':before,'content_hash':digest(records),
            'audit_hash':hashlib.sha256(meta[1].encode()).hexdigest(),'audit_entries':len(json.loads(meta[1])),
            'writer_state_hash':digest([meta[3],meta[4]]),'nodes':len(nodes),'edges':len(edges)}
        return Snapshot(nodes,edges,records,fp)
    raise PreconditionFailed('Source changed during clone export')


class CounterfactualResult(GraphModel):
    source_graph: str
    clone_graph: str
    source_fingerprint: dict[str, str | int]
    source_unchanged: bool
    clone_initial_revision: int
    clone_created_at: str
    clone_creation_wall_seconds: float
    changes: tuple[dict, ...]
    before: AnalysisResult
    after: AnalysisResult
    lost_path_ids: tuple[str, ...]
    gained_path_ids: tuple[str, ...]
    before_ranking: tuple[str, ...]
    after_ranking: tuple[str, ...]
    reservation: str = 'Hypothetical topology intervention only; not an inspection, hydraulic simulation or proof of cause.'


_OWNED = {}  # Factory-issued process-local capabilities, not enterprise RBAC.


class CounterfactualFailure(PreconditionFailed):
    def __init__(self,graph,unknown):
        self.graph=graph
        self.code='COUNTERFACTUAL_CLONE_WRITE_UNKNOWN' if unknown else 'COUNTERFACTUAL_CLONE_FAILED'
        super().__init__(f'{self.code}; retained target={graph}')


class _CloneWriter(GraphRepository):
    def __init__(self, client, name, capability):
        if capability is None or _OWNED.get(name) is not capability or not is_disposable_graph(name) or not name.startswith('civicly_b05_test_'):
            raise PreconditionFailed('Mutation requires newly owned B05 clone')
        super().__init__(client,name);self._owned_name=name;self._capability=capability

    def _authorize(self):
        if _OWNED.get(self._owned_name) is not self._capability or self.graph.name!=self._owned_name or not self.graph.name.startswith('civicly_b05_test_'):
            raise PreconditionFailed('Clone ownership changed')

    @contextmanager
    def _session(self):
        self._authorize()
        with super()._session() as session:yield session

    def remove_verified_drain(self,id,expected_hash):
        self._authorize()
        with self._session() as session:
            old=self.get_relationship(id)
            if old.kind!='DRAINS_TO' or old.properties.get('association_status')!='VERIFIED':
                raise PreconditionFailed('Counterfactual removal requires verified DRAINS_TO')
            if old.content_hash!=expected_hash:raise PreconditionFailed('Stale clone relationship hash')
            self._check_evidence(old.properties)
            # Keep identity in a map after DELETE so existing fenced commit/audit can
            # acknowledge exactly the removed stable ID without returning a deleted object.
            body='MATCH ()-[r:DRAINS_TO {id:$id,municipality_id:$scope}]->() WITH g,r,{id:r.id} AS removed DELETE r'
            self._commit(session,'edge',id,old.content_hash,body,{'id':id,'scope':self.registry.scope},'removed')
        return old


class Counterfactual:
    """Trusted internal factory; caller cannot nominate/reuse a mutation target."""
    def __init__(self,source,limits=None):
        started=time.perf_counter();self.clone_created_at=utc_now()
        self.source=source;self.limits=limits or AnalysisLimits();self.snapshot=capture(source,self.limits)
        if not self.snapshot.nodes:raise PreconditionFailed('Counterfactual source is empty')
        nodes=[{'label':n.kind,'properties':n.properties} for n in self.snapshot.nodes]
        edges=[{'type':e.kind,'source_id':e.source,'target_id':e.target,'properties':e.properties} for e in self.snapshot.edges]
        # Strict source policies/references preflight before creating any target.
        ordered=check_graph(nodes,edges,source.registry)
        self.clone_name=new_test_graph_name(5)
        if self.clone_name in source.client.list_graphs():raise PreconditionFailed('Clone target already exists')
        _OWNED[self.clone_name]=object()
        self.changes=[];self.complete=False
        try:
            if not MigrationRunner(source.client,self.clone_name).apply()['ready']:raise PreconditionFailed('Clone migration not ready')
            self._writer=_CloneWriter(source.client,self.clone_name,_OWNED[self.clone_name])
            for n in ordered:self._writer.create_node(n['label'],n['properties'])
            for e in edges:self._writer.create_relationship(e['type'],e['source_id'],e['target_id'],e['properties'])
            actual=capture(self._writer,self.limits)
            if actual.records!=self.snapshot.records:raise PreconditionFailed('Clone content differs from source')
            self.clone_initial_revision=actual.fingerprint['graph_revision'];self.assert_source_unchanged();self.complete=True;self.creation_wall_seconds=time.perf_counter()-started
        except Exception as error:
            # Deliberately retain partial clone; caller can inspect clone_name, never
            # delete source/volumes to hide a failure or repeat uncertain writes.
            raise CounterfactualFailure(self.clone_name,isinstance(error,OutcomeUnknown)) from error

    @property
    def repository(self):return self._writer

    def assert_source_unchanged(self):
        current=capture(self.source,self.limits)
        if current.fingerprint!=self.snapshot.fingerprint or current.records!=self.snapshot.records:
            raise PreconditionFailed('Source changed; counterfactual comparison invalid')
        return True

    def remove(self,id):
        if not self.complete:raise PreconditionFailed('Clone creation incomplete')
        self.assert_source_unchanged()
        if id not in self.snapshot.records:raise PreconditionFailed('Removal is outside original snapshot')
        try:old=self._writer.remove_verified_drain(id,self.snapshot.records[id])
        except OutcomeUnknown as error:
            self.changes.append({'operation':'ATTEMPTED_REMOVE_VERIFIED_DRAINS_TO','edge_id':id,'expected_hash':self.snapshot.records[id],'state':'OUTCOME_UNKNOWN','reason':'Inspect persisted edge/audit; no automatic retry'})
            raise CounterfactualFailure(self.clone_name,True) from error
        self.changes.append({'operation':'REMOVE_VERIFIED_DRAINS_TO','edge':old.model_dump(mode='json'),
                             'reason':'Explicit hypothetical edge ablation, not a source correction'})
        self.assert_source_unchanged();return old

    def add_candidate(self,source_id,target_id,properties):
        self._writer._authorize();self.assert_source_unchanged()
        if properties.get('association_status')!='CANDIDATE':raise PreconditionFailed('Only explicitly unverified candidate additions allowed')
        actual=self._writer.create_relationship('DRAINS_TO',source_id,target_id,properties)
        self.changes.append({'operation':'ADD_CANDIDATE_DRAINS_TO','edge':actual.model_dump(mode='json'),
                             'reason':'Unverified hypothetical connection; excluded from verified-only analysis'})
        self.assert_source_unchanged();return actual

    def _assert_recorded_changes(self):
        expected=dict(self.snapshot.records)
        for change in self.changes:
            if change.get('state')=='OUTCOME_UNKNOWN':raise OutcomeUnknown('Uncertain intervention must be reviewed before successful comparison')
            edge=EdgeRecord.model_validate(change['edge'])
            if change['operation']=='REMOVE_VERIFIED_DRAINS_TO':expected.pop(edge.id,None)
            elif change['operation']=='ADD_CANDIDATE_DRAINS_TO':expected[edge.id]=edge.content_hash
            else:raise PreconditionFailed('Unknown counterfactual change')
        if capture(self._writer,self.limits).records!=expected:raise PreconditionFailed('Clone contains unrecorded mutations; comparison refused')

    def compare(self,request):
        self.assert_source_unchanged();self._assert_recorded_changes()
        before=GraphAnalysis(self.source,self.limits).run(request)
        after=GraphAnalysis(self._writer,self.limits).run(request)
        self.assert_source_unchanged();self._assert_recorded_changes()
        old={p.id for p in before.paths};new={p.id for p in after.paths}
        return CounterfactualResult(source_graph=self.source.graph.name,clone_graph=self.clone_name,
            source_fingerprint=self.snapshot.fingerprint,source_unchanged=True,
            clone_initial_revision=self.clone_initial_revision,clone_created_at=self.clone_created_at,clone_creation_wall_seconds=self.creation_wall_seconds,changes=tuple(self.changes),before=before,after=after,
            lost_path_ids=tuple(sorted(old-new)),gained_path_ids=tuple(sorted(new-old)),
            before_ranking=tuple(row.id for row in before.rows),after_ranking=tuple(row.id for row in after.rows))

    def cleanup(self):
        """Explicit successful scratch cleanup only; no source or volume deletion."""
        if not self.complete:raise PreconditionFailed('Failed clone retained for inspection')
        self._writer._authorize();self.assert_source_unchanged()
        capture(self._writer,self.limits)  # Refuse cleanup while an uncertain intent remains.
        if self.clone_name in self.source.client.list_graphs():self._writer.graph.delete()
        _OWNED.pop(self.clone_name,None)
