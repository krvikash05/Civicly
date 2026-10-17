"""Trusted B04 importer: every mutation uses the accepted graph repository."""
import time
from redis.exceptions import RedisError

from app.graph.models import digest
from app.graph.repository import Conflict, NotFound, OutcomeUnknown, PreconditionFailed
from app.graph.schema import SchemaError, utc_now
from app.graph.targets import is_disposable_graph
from app.ingestion.conversion import validate_bundle, SourceError


class ImportFailure(RuntimeError):
    def __init__(self,code,report):
        super().__init__(code);self.code=code;self.report=report
        report['failure_code']=code
        if not report['errors']:report['errors'].append({'code':code})


class Importer:
    def __init__(self,repository):
        if not is_disposable_graph(repository.graph.name) or not repository.graph.name.startswith('civicly_b04_test_'):
            raise PreconditionFailed('B04 importer only permits disposable B04 graphs')
        self.repo=repository

    def run(self,bundle,*,after_record=None):
        started=time.perf_counter();report={'graph':self.repo.graph.name,'source_hash':bundle.get('source_hash') if isinstance(bundle,dict) else None,
            'started_at':utc_now(),'created':0,'matched':0,'errors':[],'latencies_seconds':[],'last_record_id':None}
        try:nodes=validate_bundle(bundle)
        except (ValueError,TypeError,KeyError) as error:
            report['errors'].append({'code':'INVALID_SOURCE','reason':str(error)})
            raise ImportFailure('INVALID_SOURCE',report) from error
        records=[('node',n) for n in nodes]+[('edge',e) for e in bundle['relationships']]
        try:
            # Recovery is proof-driven; no retry of uncertain writes occurs here.
            self.repo.recover_pending()
            for kind,record in records:
                at=time.perf_counter();id=record['properties']['id'];report['last_record_id']=id
                expected=bundle['manifest']['record_hashes'][id]
                get=self.repo.get_node if kind=='node' else self.repo.get_relationship
                try:existing=get(id)
                except NotFound:existing=None
                if existing is not None:
                    if existing.content_hash!=expected:raise Conflict('Changed record requires explicit conflict/update/version review')
                    report['matched']+=1
                else:
                    try:
                        if kind=='node':actual=self.repo.create_node(record['label'],record['properties'])
                        else:actual=self.repo.create_relationship(record['type'],record['source_id'],record['target_id'],record['properties'])
                        if actual.content_hash!=expected:raise Conflict('Concurrent post-write content differs from source')
                        report['created']+=1
                    except Conflict:
                        # A concurrent equal writer may win CREATE; reread actual persisted content.
                        if get(id).content_hash!=expected:raise
                        report['matched']+=1
                report['latencies_seconds'].append(time.perf_counter()-at)
                if after_record is not None:after_record(kind,id,report)
        except OutcomeUnknown as error:
            report['errors'].append({'code':'DATABASE_OUTCOME_UNKNOWN','id':report['last_record_id']})
            report['wall_seconds']=time.perf_counter()-started
            raise ImportFailure('DATABASE_OUTCOME_UNKNOWN',report) from error
        except RedisError as error:
            report['errors'].append({'code':'DATABASE_UNAVAILABLE','id':report['last_record_id']})
            report['wall_seconds']=time.perf_counter()-started
            raise ImportFailure('DATABASE_UNAVAILABLE',report) from error
        except (Conflict,PreconditionFailed,SchemaError,NotFound) as error:
            report['errors'].append({'code':'SOURCE_CONFLICT_OR_PRECONDITION','id':report['last_record_id'],'reason':str(error)})
            report['wall_seconds']=time.perf_counter()-started
            raise ImportFailure('SOURCE_CONFLICT_OR_PRECONDITION',report) from error
        try:
            # Full bounded identity/content verification, not just successful write counts.
            actual={}
            for kind,record in records:
                id=record['properties']['id'];get=self.repo.get_node if kind=='node' else self.repo.get_relationship
                actual[id]=get(id).content_hash
            if actual!=bundle['manifest']['record_hashes']:raise ImportFailure('CONTENT_VERIFICATION_FAILED',report)
            counts=self.repo.graph.ro_query('MATCH (n:CivicEntity) RETURN count(n)',timeout=1000).result_set[0][0]
            edge_count=self.repo.graph.ro_query('MATCH ()-[r]->() RETURN count(r)',timeout=1000).result_set[0][0]
            if counts!=len(nodes) or edge_count!=len(bundle['relationships']):raise ImportFailure('UNEXPECTED_GRAPH_RECORDS',report)
            state=self.repo.graph.ro_query("MATCH (m:CivicSchemaMigration {id:$id}) RETURN coalesce(m.repo_revision,0),coalesce(m.repo_audit,'[]'),coalesce(m.repo_pending,'')",params={'id':'0001'},timeout=1000).result_set[0]
            if state[2]:raise ImportFailure('DATABASE_OUTCOME_UNKNOWN',report)
            import json
            report.update(wall_seconds=time.perf_counter()-started,completed_at=utc_now(),graph_revision=state[0],
                audit_entries=len(json.loads(state[1])),audit_bytes=len(state[1].encode()),node_count=counts,relationship_count=edge_count,
                verified_content_hash=digest(actual))
            return report
        except RedisError as error:
            report['errors'].append({'code':'DATABASE_UNAVAILABLE','phase':'FINAL_VERIFICATION'})
            report['wall_seconds']=time.perf_counter()-started
            raise ImportFailure('DATABASE_UNAVAILABLE',report) from error
