"""Controlled trace service and compatible additive storage migration."""
import json,hashlib
from pathlib import Path
from app.graph.migration import MigrationRunner,MigrationError
from app.graph.repository import GraphRepository,Conflict
from app.graph.schema import utc_now,Registry
from app.graph.targets import is_disposable_graph
from app.mcp.runtime import ROOT,CITY_GRAPH
from .models import TraceRecord
from .contracts import digest

PLAN=ROOT/'backend/app/graph/migrations/0002_mcp_traces.json'


def trace_target(name):
    if not is_disposable_graph(name) or not name.startswith('civicly_b07_test_') or name==CITY_GRAPH:
        raise ValueError('Explicit B07 trace capability required')
    return name


class ScopedClient:
    """Adapter lists only its exact key after real readiness read; never GRAPH.LIST."""
    def __init__(self,client,name):self.__client=client;self.name=name;self.connection=client.connection
    def select_graph(self,name):
        if name!=self.name:raise ValueError('Graph capability denied')
        return self.__client.select_graph(name)
    def list_graphs(self):
        rows=self.select_graph(self.name).ro_query('MATCH (m:CivicSchemaMigration {id:$id}) RETURN m.state LIMIT 1',params={'id':'0001'},timeout=1000).result_set
        return [self.name] if rows else []


class TraceMigration:
    def __init__(self,client,name):
        self.name=trace_target(name);self.client=client;self.base=MigrationRunner(client,name)
        self.plan=json.loads(PLAN.read_text());self.checksum=hashlib.sha256(PLAN.read_bytes()).hexdigest()
        if self.base.checksum!=self.plan['requires_0001_sha256']:raise MigrationError('0001 compatibility mismatch')
        self.graph=client.select_graph(name)
    def status(self):
        row=self.graph.ro_query('MATCH (m:CivicMCPTraceMigration {id:$id}) RETURN m.checksum,m.state LIMIT 2',params={'id':'0002'},timeout=1000).result_set
        if len(row)>1 or (row and row[0][1] not in {'APPLYING','FAILED','READY'}):raise MigrationError('Trace migration history invalid')
        if row and row[0][0]!=self.checksum:raise MigrationError('Trace migration checksum mismatch')
        ready=bool(row and row[0][1]=='READY')
        if ready:
            for kind in ('indexes','constraints'):
                for spec in self.plan[kind]:self.base._wait(kind,spec,seconds=.1)
        return {'graph':self.name,'id':'0002','family':self.plan['family'],'ready':ready,'checksum':self.checksum}
    def apply(self,retry_failed=False):
        if not self.base.status()['ready']:raise MigrationError('0001 prerequisite not READY')
        lock=self.client.connection.lock('civicly:trace-migration:'+self.name,timeout=30,blocking=False)
        if not lock.acquire():raise MigrationError('Trace migration busy')
        def record(state):
            self.graph.query('MERGE (m:CivicMCPTraceMigration {id:$id}) SET m.checksum=$hash,m.state=$state,m.updated_at=$now RETURN m.id',params={'id':'0002','hash':self.checksum,'state':state,'now':utc_now()},timeout=1000)
        recorded=False
        try:
            current=self.status()
            if current['ready']:return current
            record('APPLYING');recorded=True
            for spec in self.plan['indexes']:self.base._ensure_index(spec)
            for spec in self.plan['constraints']:self.base._ensure_constraint(spec,retry_failed)
            record('READY');return self.status()
        except Exception:
            if recorded:record('FAILED')
            raise
        finally:lock.release()


class TraceStore:
    def __init__(self,client,name):
        self.name=trace_target(name)
        scoped=ScopedClient(client,name)
        self.repo=GraphRepository(scoped,name)
        if not TraceMigration(scoped,name).status()['ready']:raise MigrationError('Trace storage not READY')
    def get(self,id):
        rows=self.repo._read('MATCH (n:ToolExecution {id:$id}),(d:CivicMCPTraceDetail {id:$id}) RETURN properties(n),d.payload_json,d.payload_sha256 LIMIT 2',{'id':id})
        if not rows:return None
        if len(rows)!=1:raise Conflict('Duplicate trace ID')
        props,raw,sha=rows[0];self.repo.registry.validate_node('ToolExecution',props)
        record=TraceRecord.model_validate_json(raw)
        if digest(json.loads(raw))!=sha or record.context.execution_id!=id:raise Conflict('Trace hash/identity mismatch')
        expected={'trace_id':record.context.trace_id,'status':record.status,'tool_name':record.tool_name,'started_at':record.started_at,'finished_at':record.finished_at,'input_digest':record.arguments_sha256}
        if any(props.get(k)!=v for k,v in expected.items()) or props.get('output_digest')!=record.output_sha256 or props.get('error_code')!=record.error_code:
            raise Conflict('Core trace/detail mismatch')
        return record
    def append(self,record):
        if not isinstance(record,TraceRecord):raise TypeError('Validated trace required')
        raw=record.model_dump_json();payload=json.loads(raw);sha=digest(payload)
        if len(raw.encode())>65536:raise ValueError('Trace byte budget')
        id=record.context.execution_id;now=record.finished_at
        props={'id':id,'schema_version':3,'municipality_id':'demo-city','created_at':now,'updated_at':now,
            'tool_name':record.tool_name,'started_at':record.started_at,'finished_at':now,'status':record.status,
            'trace_id':record.context.trace_id,'input_digest':record.arguments_sha256}
        if record.output_sha256:props['output_digest']=record.output_sha256
        if record.error_code:props['error_code']=record.error_code
        self.repo.registry.validate_node('ToolExecution',props)
        with self.repo._session() as session:
            old=self.get(id)
            if old:
                if digest(old.model_dump(mode='json'))!=sha:raise Conflict('Trace ID payload conflict')
                return id
            self.repo._commit(session,'node',id,'',
                'CREATE (n:CivicEntity:ToolExecution) SET n=$props CREATE (d:CivicMCPTraceDetail) SET d=$detail',
                {'props':props,'detail':{'id':id,'payload_json':raw,'payload_sha256':sha}},'n')
        saved=self.get(id)
        if saved!=record:raise Conflict('Trace persistence verification failed')
        return id
