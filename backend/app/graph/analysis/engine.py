"""Deterministic aggregation of bounded, typed FalkorDB paths."""
from collections import defaultdict
import heapq
import time
from app.graph.repository import PreconditionFailed
from .models import AnalysisLimits, AnalysisRequest, CaseRequest, AnalysisResult, AnalysisRow
from .reader import Reader, AnalysisBudgetExceeded


def topological_order(ids, dependencies, step=lambda:None):
    """DEPENDS_ON is dependent->prerequisite: emit prerequisites first."""
    ids=set(ids);need={id:set() for id in ids};dependents=defaultdict(set)
    for dependent,prerequisite in dependencies:
        step()
        if dependent not in ids or prerequisite not in ids:raise PreconditionFailed('Unresolved dependency endpoint')
        need[dependent].add(prerequisite);dependents[prerequisite].add(dependent)
    ready=[id for id in ids if not need[id]];heapq.heapify(ready);result=[]
    while ready:
        step();id=heapq.heappop(ready);result.append(id)
        for child in sorted(dependents[id]):
            need[child].remove(id)
            if not need[child]:heapq.heappush(ready,child)
    if len(result)!=len(ids):raise PreconditionFailed('Cycle in stored dependency export')
    return tuple(result)


class GraphAnalysis:
    def __init__(self, repository, limits=None):
        self.repository=repository;self.limits=limits or AnalysisLimits()

    def _execute(self, request, work):
        if request.max_hops>self.limits.max_hops:raise AnalysisBudgetExceeded('Hop request exceeds configuration')
        meter={'queries':0,'steps':0,'started':time.perf_counter()}
        for attempt in range(2):
            reader=Reader(self.repository,request,self.limits,meter);before=reader.state()
            rows,gaps=work(reader)
            after=reader.state()
            if before!=after:continue
            truncated=reader.truncated or len(rows)>request.limit
            if reader.excluded_future_evidence:gaps.append('Paths excluded because supporting evidence is outside knowledge time')
            if truncated:gaps.append('Result/export cap reached; counts and ranks are partial lower bounds')
            reservations=['Connectivity and count-based criticality are not root-cause or hydraulic proof.',
                          'No result is a bounded negative, not proof of global disconnection.',
                          'Historical node versions are not reconstructed; future-updated records are excluded.',
                          'Open relationship validity bounds remain unknown, not manufactured dates.']
            if request.include_candidates:reservations.append('Exploratory topology includes explicit CANDIDATE and REPORTED claims as well as VERIFIED; not established connectivity.')
            return AnalysisResult(operation='case_retrieval' if isinstance(request,CaseRequest) else request.operation,
                graph=self.repository.graph.name,graph_revision=before,as_of=request.as_of,include_candidates=request.include_candidates,
                rows=tuple(rows[:request.limit]),nodes=tuple(reader.nodes[id] for id in sorted(reader.nodes)),
                edges=tuple(reader.edges[id] for id in sorted(reader.edges)),paths=tuple(reader.proofs[id] for id in sorted(reader.proofs)),
                truncated=truncated,search_limited=True,gaps=tuple(dict.fromkeys(gaps)),reservations=tuple(reservations),
                budgets={**self.limits.model_dump(), 'requested_total_hops':request.max_hops,
                         'infrastructure_hops':request.max_hops-1 if getattr(request,'operation',None)=='shared_downstream' else request.max_hops},
                measurements={'queries':meter['queries'],'computation_steps':meter['steps'],
                              'wall_seconds':time.perf_counter()-meter['started'],'snapshot_retries':attempt,
                              'future_evidence_paths_excluded':reader.excluded_future_evidence})
        raise PreconditionFailed('Source changed during read analysis; retry later')

    def run(self, request):
        if not isinstance(request,AnalysisRequest):raise TypeError('Use typed AnalysisRequest')
        return self._execute(request,lambda r:self._work(r,request))

    def cases(self, request):
        if not isinstance(request,CaseRequest):raise TypeError('Use typed CaseRequest')
        from .cases import retrieve
        return self._execute(request,lambda r:retrieve(r,request))

    def _work(self,r,q):
        gaps=[];op=q.operation;rows=[]
        if op=='shared_downstream':
            coverage=defaultdict(set);proofs=defaultdict(set);distances=defaultdict(list)
            for id in q.incident_ids:
                r.root(id,'Incident')
                for p in r.paths('incident_down',id=id):
                    target=p.node_ids[-1];coverage[target].add(id);proofs[target].add(p.id);distances[target].append(len(p.edge_ids))
            for id in sorted(coverage,key=lambda x:(-len(coverage[x]),max(distances[x]),x)):
                if len(coverage[id])>=q.threshold:rows.append(AnalysisRow(id=id,related_ids=tuple(sorted(coverage[id])),
                    factors={'distinct_incident_coverage':len(coverage[id]),'maximum_total_hops':max(distances[id])},path_ids=tuple(sorted(proofs[id]))))
        elif op=='task_dag':
            roots=list(q.ids);members=set(roots)
            if q.plan_id:
                r.root(q.plan_id,'ResolutionPlan')
                paths=r.paths('plan_tasks',id=q.plan_id);roots=sorted({p.node_ids[-1] for p in paths});members=set(roots)
                if len(roots)>20:raise AnalysisBudgetExceeded('Plan exceeds20 task roots')
            for id in roots:r.root(id,'ActionTask');r.paths('tasks',id=id)
            tasks={n.id for n in r.nodes.values() if n.kind=='ActionTask'}
            deps=[(e.source,e.target) for e in r.edges.values() if e.kind=='DEPENDS_ON']
            order=topological_order(tasks,deps,r.step)
            for position,id in enumerate(order):
                required=sorted(t for s,t in deps if s==id)
                rows.append(AnalysisRow(id=id,related_ids=tuple(required),factors={'topological_position':position,
                    'external_to_plan':id not in members,'unmet_prerequisites':sum(r.nodes[t].properties['status']!='COMPLETED' for t in required),
                    'dag_valid_within_export':True},path_ids=tuple(sorted(p.id for p in r.proofs.values() if id in p.node_ids))))
            gaps.append('Ordering validates the bounded exported DAG only; unexported dependencies are not ruled out')
        else:
            paths_by_root={}
            for id in q.ids:
                n=r.root(id)
                if 'InfrastructureAsset' not in n.labels and not (op in ('components','dependencies') and n.kind=='CollectionRoute'):
                    raise PreconditionFailed('Physical algorithm requires infrastructure/route root')
                template='weak' if op=='components' else 'dependencies' if op=='dependencies' else 'up' if op=='reachability' and q.direction=='upstream' else 'down'
                paths_by_root[id]=r.paths(template,id=id)
            if op=='components':
                adjacency=defaultdict(set);network=set(q.ids)
                for p in r.proofs.values():
                    network.update(p.node_ids)
                    for a,b in zip(p.node_ids,p.node_ids[1:]):adjacency[a].add(b);adjacency[b].add(a)
                seen=set()
                for id in sorted(network):
                    if id in seen:continue
                    todo=[id];component=set()
                    while todo:
                        r.step();n=todo.pop()
                        if n in component:continue
                        component.add(n);todo.extend(adjacency[n]-component)
                    seen|=component
                    rows.append(AnalysisRow(id=min(component),related_ids=tuple(sorted(component)),
                        factors={'induced_component_size':len(component),'direction_ignored_for_membership_only':True},
                        path_ids=tuple(sorted(p.id for p in r.proofs.values() if set(p.node_ids)<=component))))
                gaps.append('Components partition the induced bounded export, not the entire municipality')
            else:
                for id,paths in paths_by_root.items():
                    targets=sorted({p.node_ids[-1] for p in paths}-{id})
                    rows.append(AnalysisRow(id=id,related_ids=tuple(targets),factors={'distinct_reachable_entities':len(targets),
                        'distinct_infrastructure_assets':sum('InfrastructureAsset' in r.nodes[t].labels for t in targets),
                        'direction':q.direction if op=='reachability' else 'downstream',
                        'maximum_total_hops':max((len(p.edge_ids) for p in paths),default=0)},path_ids=tuple(sorted(p.id for p in paths))))
                if op=='criticality':rows.sort(key=lambda row:(-row.factors['distinct_infrastructure_assets'],row.id))
                if op=='impacted_assets':gaps.append('Potential failure coverage is directed downstream exposure, not a flood/causal prediction; upstream hydraulic effects are not simulated')
        if not r.proofs and op!='task_dag':gaps.append('No qualifying paths within evidence/time/search filters; missing proof and actual disconnection are not distinguished')
        return rows,gaps
