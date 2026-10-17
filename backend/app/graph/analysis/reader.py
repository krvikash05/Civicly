"""Private fixed templates; all source reads use bounded GRAPH.RO_QUERY."""
import time
from app.graph.models import EdgeRecord, digest
from app.graph.queries import GraphQueries
from app.graph.repository import PreconditionFailed, OutcomeUnknown, NotFound
from app.graph.schema import timestamp
from .models import ProofPath


class AnalysisBudgetExceeded(PreconditionFailed):
    code = 'ANALYSIS_BUDGET_EXCEEDED'


class Reader:
    def __init__(self, repo, request, limits, meter):
        self.repo, self.request, self.limits, self.meter = repo, request, limits, meter
        self.nodes, self.edges, self.proofs, self.cache = {}, {}, {}, {}
        self.truncated = False
        self.excluded_future_evidence = 0
        self.params = {'scope':repo.registry.scope,'as_of':timestamp(request.as_of).strftime('%Y-%m-%dT%H:%M:%S.%f'),
                       'hops':request.max_hops,'physical':repo.policy['verified_associations'],
                       'statuses':['VERIFIED','CANDIDATE','REPORTED'] if request.include_candidates else ['VERIFIED']}

    def step(self, count=1):
        self.meter['steps'] += count
        if self.meter['steps']>self.limits.max_steps:raise AnalysisBudgetExceeded('Computation step budget reached')
        if time.perf_counter()-self.meter['started']>self.limits.wall_seconds:raise AnalysisBudgetExceeded('Analysis wall budget reached')

    def query(self, query, params=None):
        self.step();self.meter['queries']+=1
        if self.meter['queries']>self.limits.max_queries:raise AnalysisBudgetExceeded('Read query budget reached')
        result=self.repo.graph.ro_query(query,params={**self.params,**(params or {})},timeout=self.limits.timeout_ms).result_set
        self.step();return result

    def state(self):
        rows=self.query("MATCH (m:CivicSchemaMigration {id:$id}) WHERE m.state='READY' RETURN coalesce(m.repo_revision,0),coalesce(m.repo_pending,'') LIMIT 1",{'id':'0001'})
        if not rows or rows[0][1]:raise OutcomeUnknown('Pending source mutation; reconcile before analysis')
        return rows[0][0]

    def visible(self, properties):
        at=timestamp(self.request.as_of)
        fields=('created_at','updated_at','observed_at','recorded_at','started_at','opened_at',
                'assessed_at','evaluated_at','completed_at','requested_at','reported_at','actual_at','ended_at','first_seen_at')
        return (all(timestamp(properties[f])<=at for f in fields if f in properties)
                and ('valid_from' not in properties or timestamp(properties['valid_from'])<=at)
                and ('valid_to' not in properties or at<timestamp(properties['valid_to'])))

    def node(self, id, kind=None):
        if id not in self.cache:
            rows=self.query('MATCH (n:CivicEntity {id:$id,municipality_id:$scope}) RETURN labels(n),properties(n) LIMIT 2',{'id':id})
            if len(rows)!=1:raise NotFound('Unique analysis node not found')
            self.cache[id]=self.repo.decode_node(*rows[0])
        n=self.cache[id]
        if kind and kind not in n.labels:raise PreconditionFailed('Analysis root type mismatch')
        return n

    def root(self, id, kind=None):
        n=self.node(id,kind)
        if not self.visible(n.properties):raise PreconditionFailed('Root is outside knowledge/validity time')
        if len(self.nodes)>=self.limits.max_nodes and id not in self.nodes:raise AnalysisBudgetExceeded('Root node cap reached')
        self.nodes[id]=n;return n

    def _evidence(self, edge):
        id=edge.properties.get('source_evidence_id')
        if not id:return None
        ev=self.node(id,'Evidence');p=ev.properties
        # Same proof conditions as repository._check_evidence, with a per-analysis cache.
        if edge.properties.get('association_status')=='VERIFIED':
            if p['reliability']!='VERIFIED' or p['source_kind']=='AGENT' or not p.get('observed_at') or not p.get('source_record_id'):
                raise PreconditionFailed('Stored verified edge lacks dated attributed proof')
            if any(timestamp(p[f])>timestamp(edge.properties['created_at']) for f in ('created_at','recorded_at','observed_at')):
                raise PreconditionFailed('Stored verified edge cites future proof')
        return ev

    def _condition(self):
        condition=GraphQueries._time_filter()
        # Event knowledge fields additional to the accepted B03 path reader.
        key=GraphQueries._time_key
        condition+=' AND all(n IN nodes(p) WHERE '+ ' AND '.join(f'(n.{f} IS NULL OR {key("n."+f)}<=$as_of)' for f in ('reported_at','actual_at','ended_at','first_seen_at'))+')'
        return condition+' AND all(e IN relationships(p) WHERE NOT type(e) IN $physical OR e.association_status IN $statuses)'

    def paths(self, template, **params):
        h=params.pop('_hops',self.request.max_hops)
        if type(h) is not int or not 1<=h<=self.request.max_hops:raise PreconditionFailed('Invalid internal hop budget')
        networks={'drain':'DRAINS_TO','dependencies':'DRAINS_TO|UNDERLIES|COLLECTED_BY'}
        patterns={
            'down':f'(a:InfrastructureAsset {{id:$id}})-[:DRAINS_TO*1..{h}]->(b:InfrastructureAsset)',
            'up':f'(a:InfrastructureAsset {{id:$id}})<-[:DRAINS_TO*1..{h}]-(b:InfrastructureAsset)',
            'dependencies':f'(a:CivicEntity {{id:$id}})-[:{networks["dependencies"]}*1..{h}]->(b:CivicEntity)',
            'weak':f'(a:CivicEntity {{id:$id}})-[:{networks["dependencies"]}*1..{h}]-(b:CivicEntity)',
            'incident_down':f'(i:Incident {{id:$id}})-[:AFFECTS]->(a:InfrastructureAsset)-[:DRAINS_TO*0..{max(0,h-1)}]->(b:InfrastructureAsset)',
            'seed_context':'(i:Incident {id:$id})-[:AFFECTS|OCCURRED_AT|PART_OF]->(b:CivicEntity)',
            'plan_tasks':'(p0:ResolutionPlan {id:$id})-[:HAS_TASK]->(t:ActionTask)',
            'tasks':f'(t:ActionTask {{id:$id}})-[:DEPENDS_ON*1..{h}]->(d:ActionTask)',
            'case_asset':'(i:Incident)-[:AFFECTS]->(a:InfrastructureAsset)',
            'case_zone':'(i:Incident)-[:OCCURRED_AT]->(l:Location)-[:IN_ZONE]->(z:Zone)',
            'case_cluster':'(i:Incident)-[:PART_OF]->(c:ProblemCluster)',
            'case_issue':'(i:Incident)',
            'case_context':'(i:Incident)-[:AFFECTS|OCCURRED_AT|PART_OF]->(b:CivicEntity)',
            'zone_context':'(l:Location)-[:IN_ZONE]->(z:Zone)',
            'inspection':'(a:InfrastructureAsset)<-[:INSPECTS]-(ins:Inspection)',
            'inspection_evidence':'(a:InfrastructureAsset)<-[:INSPECTS]-(ins:Inspection)-[:PRODUCED]->(ev:Evidence)',
            'work_order':'(a:InfrastructureAsset)<-[:TARGETS]-(t:ActionTask)<-[:IMPLEMENTS]-(wo:WorkOrder)',
            'outcome':'(a:InfrastructureAsset)<-[:TARGETS]-(t:ActionTask)<-[:IMPLEMENTS]-(wo:WorkOrder)-[:RESULTED_IN]->(out:InterventionOutcome)',
        }
        filters={
            'case_asset':'a.id IN $assets', 'case_zone':'z.id=$zone',
            'case_cluster':'c.id IN $clusters','case_issue':'i.issue_type=$issue',
            'case_context':'i.id IN $incidents','zone_context':'l.id IN $locations',
            'inspection':'a.id IN $assets','inspection_evidence':'a.id IN $assets',
            'work_order':'a.id IN $assets','outcome':'a.id IN $assets',
        }
        if template not in patterns:raise PreconditionFailed('Unknown internal analysis template')
        if len(self.proofs)>=self.limits.max_paths:
            self.truncated=True;return []
        condition=self._condition()
        if template in filters:condition+=' AND '+filters[template]
        if template.startswith('case_') and template!='case_context':
            condition+=' AND ($after IS NULL OR $after<='+GraphQueries._time_key('i.started_at')+') AND '+GraphQueries._time_key('i.started_at')+'<$before AND ($exclude IS NULL OR i.id<>$exclude)'
        query='MATCH p='+patterns[template]+' WHERE '+condition+' RETURN nodes(p),relationships(p) ORDER BY length(p) LIMIT $fetch'
        rows=self.query(query,{**params,'fetch':self.limits.max_paths+1})
        if len(rows)>self.limits.max_paths:self.truncated=True
        accepted=[]
        for ns,es in rows[:self.limits.max_paths]:
            self.step()
            records=[self.repo.decode_node(n.labels,n.properties) for n in ns]
            internal={n.id:r for n,r in zip(ns,records,strict=True)};edges=[];evidence={}
            for e in es:
                s,t=internal[e.src_node],internal[e.dest_node]
                props=dict(e.properties)
                self.repo.registry.validate_edge(e.relation,s.kind,s.properties,t.kind,t.properties,props)
                edge=EdgeRecord(id=props['id'],kind=e.relation,source=s.id,target=t.id,properties=props)
                ev=self._evidence(edge)
                if ev is not None:evidence[ev.id]=ev
                edges.append(edge)
            if any(not self.visible(ev.properties) for ev in evidence.values()):
                self.excluded_future_evidence+=1;continue
            ids=tuple(n.id for n in records);eids=tuple(e.id for e in edges)
            pathid='PATH-'+digest([ids,eids])[:32]
            if (len(set(self.nodes)|set(ids)|evidence.keys())>self.limits.max_nodes or
                len(set(self.edges)|set(eids))>self.limits.max_edges or
                (pathid not in self.proofs and len(self.proofs)>=self.limits.max_paths)):
                self.truncated=True;break
            for n in [*records,*evidence.values()]:
                if n.id in self.nodes and self.nodes[n.id].content_hash!=n.content_hash:raise PreconditionFailed('Inconsistent node content within snapshot')
                self.nodes[n.id]=n;self.cache[n.id]=n
            for e in edges:
                if e.id in self.edges and self.edges[e.id].content_hash!=e.content_hash:raise PreconditionFailed('Ambiguous edge within snapshot')
                self.edges[e.id]=e
            proof=ProofPath(id=pathid,node_ids=ids,edge_ids=eids,
                directions=tuple('OUTGOING' if e.source==ids[i] else 'INCOMING' for i,e in enumerate(edges)),
                evidence_ids=tuple(sorted(evidence.keys()|{n.id for n in records if n.kind=='Evidence'})),
                context={'template':template,'classification':'Connectivity/evidence context, not causal proof'})
            self.proofs[pathid]=proof;accepted.append(proof)
        return accepted
