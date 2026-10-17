"""Bounded RO context, accepted B03 histories and B05 verified topology."""
from datetime import timedelta
import json,time
from app.graph.queries import GraphQueries
from app.graph.models import QueryRequest
from app.graph.analysis.engine import GraphAnalysis
from app.graph.analysis.models import AnalysisRequest
from app.graph.repository import PreconditionFailed
from app.graph.schema import timestamp
from .models import Assessment,Journal,HistorySummary
from app.graph.models import digest


def visible(props,at):
    instant=timestamp(at)
    fields=('created_at','updated_at','observed_at','recorded_at','started_at','requested_at','evaluated_at','completed_at','actual_at')
    return all(timestamp(props[k])<=instant for k in fields if k in props) and ('valid_from' not in props or timestamp(props['valid_from'])<=instant) and ('valid_to' not in props or instant<timestamp(props['valid_to']))

class Reader:
    def __init__(self,repo,as_of):
        self.repo,self.as_of=repo,as_of;self.started=time.monotonic();self.queries=0
        self.paths=[];self.topology=[];self.gaps=[]
    def check(self,n=1):
        self.queries+=n
        if self.queries>96 or time.monotonic()-self.started>8:raise PreconditionFailed('B08 context budget exceeded; no incomplete matching write')
    def read(self,query,params,limit):
        self.check();rows=self.repo._read(query,{**params,'limit':limit+1})
        if len(rows)>limit:raise PreconditionFailed('B08 context scan truncated; review before intake')
        return rows
    def node(self,id,kind=None):
        self.check();node=self.repo.get_node(id,kind)
        if not visible(node.properties,self.as_of):raise PreconditionFailed('Referenced record outside knowledge time')
        return node
    def references(self,q):
        self.node(q.location_id,'Location')
        assets=[self.node(id,'InfrastructureAsset') for id in q.asset_ids]
        if q.issue_type=='ROAD_DAMAGE' and assets and not any('RoadSegment' in a.labels for a in assets):raise PreconditionFailed('Road damage requires explicit road assets')
        if q.issue_type=='WASTE_ACCUMULATION' and assets and not any('WasteCollectionPoint' in a.labels for a in assets):raise PreconditionFailed('Waste reports require collection-point assets')
        self.asset_labels={a.id:set(a.labels) for a in assets}
        if q.asset_ids:
            rows=self.read('MATCH (a:InfrastructureAsset)-[r:LOCATED_AT|SERVES]->(l:Location) WHERE a.id IN $ids RETURN type(r),properties(r),labels(a),properties(a),labels(l),properties(l) LIMIT $limit',{'ids':q.asset_ids},30)
            locations={id:set() for id in q.asset_ids}
            for row in rows:
                e=self.repo._decode_edge_row(row)
                if visible(e.properties,self.as_of):locations[e.source].add(e.target)
            for id,known in locations.items():
                if known and q.location_id not in known:self.gaps.append('Reported location conflicts with inventory context for '+id+'; association remains REPORTED.')
        for id in sorted(set(q.evidence_ids)|{m.evidence_id for m in q.details.measurements if m.evidence_id}):self.node(id,'Evidence')
        return assets
    def dependencies(self,q):
        related=set(q.asset_ids);roots=set(q.asset_ids)
        # Incoming lookup only discovers roots for the unchanged B05 forward engine;
        # it never reverses a physical edge or treats a candidate as verified.
        for id in q.asset_ids:
            rows=self.read('MATCH (s:InfrastructureAsset)-[:UNDERLIES]->(a:InfrastructureAsset {id:$id}) RETURN s.id LIMIT $limit',{'id':id},6)
            roots.update(row[0] for row in rows)
        if len(roots)>9:raise PreconditionFailed('Dependency root budget exceeded')
        for id in sorted(roots):
            self.check()
            result=GraphAnalysis(self.repo).run(AnalysisRequest(operation='dependencies',ids=(id,),as_of=self.as_of,max_hops=4,include_candidates=False))
            self.check(int(result.measurements['queries']))
            if result.truncated:raise PreconditionFailed('Topology export truncated; no automatic grouping')
            self.topology.extend(result.paths);self.paths.extend(result.paths)
            related.update(n.id for n in result.nodes if 'InfrastructureAsset' in n.labels)
        for id in q.asset_ids:
            self.check()
            result=GraphAnalysis(self.repo).run(AnalysisRequest(operation='reachability',ids=(id,),as_of=self.as_of,direction='upstream',max_hops=4,include_candidates=False))
            self.check(int(result.measurements['queries']))
            if result.truncated:raise PreconditionFailed('Upstream context truncated; no automatic grouping')
            self.topology.extend(result.paths);self.paths.extend(result.paths)
            related.update(n.id for n in result.nodes if 'InfrastructureAsset' in n.labels)
        return related
    def candidates(self,q):
        related=self.dependencies(q);key=GraphQueries._time_key
        params={'location':q.location_id,'assets':sorted(related),'as_of':timestamp(self.as_of).strftime('%Y-%m-%dT%H:%M:%S.%f')}
        # Separate bounded branches; fail closed on overflow instead of arbitrary sampling.
        bodies=["MATCH (i:Incident)-[r:OCCURRED_AT]->(l:Location {id:$location})",
                'MATCH (i:Incident)-[r:AFFECTS]->(a:InfrastructureAsset) WHERE a.id IN $assets']
        found={}
        for body in bodies:
            rows=self.read(body+(' AND ' if ' WHERE ' in body else ' WHERE ')+key('i.started_at')+'<=$as_of RETURN labels(i),properties(i) ORDER BY i.started_at ASC,i.id ASC LIMIT $limit',params,100)
            for labels,props in rows:
                n=self.repo.decode_node(labels,props)
                if visible(n.properties,self.as_of):found[n.id]=n
        if len(found)>100:raise PreconditionFailed('Incident context exceeds100; no incomplete match')
        contexts={id:{'node':n,'assets':set(),'locations':set(),'clusters':set(),'events':set(),'edges':[]} for id,n in found.items()}
        if not found:return contexts
        rows=self.read('MATCH (i:Incident)-[r:AFFECTS|OCCURRED_AT|PART_OF]->(n:CivicEntity) WHERE i.id IN $ids RETURN type(r),properties(r),labels(i),properties(i),labels(n),properties(n) LIMIT $limit',{'ids':sorted(found)},400)
        for row in rows:
            e=self.repo._decode_edge_row(row);n=self.repo.decode_node(row[4],row[5])
            if not visible(e.properties,self.as_of) or not visible(n.properties,self.as_of):continue
            ev=self.repo._check_evidence(e.properties)
            if ev and not visible(ev.properties,self.as_of):continue
            kind={'AFFECTS':'assets','OCCURRED_AT':'locations','PART_OF':'clusters'}[e.kind]
            contexts[e.source][kind].add(e.target);contexts[e.source]['edges'].append(e)
        rows=self.read('MATCH (c:Complaint)-[r:REPORTS]->(i:Incident) WHERE i.id IN $ids OPTIONAL MATCH (v:Evidence {id:r.source_evidence_id}) RETURN i.id,properties(v) LIMIT $limit',{'ids':sorted(found)},200)
        for id,props in rows:
            if props and props.get('evidence_type')=='COMPLAINT_INTAKE' and visible(props,self.as_of):
                self.repo.registry.validate_node('Evidence',props)
                journal=Journal.model_validate_json(props['summary'])
                if digest(journal.canonical)!=journal.request_hash:raise PreconditionFailed('Corrupt intake context journal')
                if journal.state=='COMMITTED' and journal.canonical.get('event_reference'):
                    contexts[id]['events'].add((journal.canonical['source_id'],journal.canonical['event_reference']))
        return contexts
    def members(self,cluster):
        rows=self.read('MATCH (i:Incident)-[r:PART_OF]->(c:ProblemCluster {id:$id}) RETURN type(r),properties(r),labels(i),properties(i),labels(c),properties(c) LIMIT $limit',{'id':cluster},100)
        result=[]
        for row in rows:
            e=self.repo._decode_edge_row(row);n=self.repo.decode_node(row[2],row[3])
            if visible(e.properties,self.as_of) and visible(n.properties,self.as_of):result.append(n)
        return result
    def assessment(self,q):
        a=Assessment(measurements=[m.canonical() for m in q.details.measurements],claims=q.details.claims)
        groups={}
        for m in a.measurements:groups.setdefault((m['name'],m['observed_at']),set()).add(m['value'])
        for (name,at),values in groups.items():
            if len(values)>1:a.contradictions.append('Conflicting reported '+name+' at '+at+'; no arbitrary winner or averaging.')
        gaps=['Submitted measurements/claims are source reports, not verified observations or causal findings.']
        if not q.asset_ids:gaps.append('No explicit infrastructure asset reference; location alone cannot establish physical connectivity.')
        if q.subtype=='UNSPECIFIED':gaps.append('Issue subtype unspecified; matching is qualified.')
        names={m.name for m in q.details.measurements}
        expected={'WATERLOGGING':['water_depth','duration','rainfall'],'ROAD_DAMAGE':['pothole_depth','damage_area'],'WASTE_ACCUMULATION':['waste_quantity']}[q.issue_type]
        gaps += [name+' measurement missing; no quantity manufactured.' for name in expected if name not in names]
        history=[];evs=set(q.evidence_ids)|{m.evidence_id for m in q.details.measurements if m.evidence_id}
        if q.issue_type=='WATERLOGGING':
            if 'rainfall' in names and (not q.details.rainfall_station_reference or not q.details.rainfall_from or not q.details.rainfall_to):gaps.append('Rainfall station/interval incomplete; cannot attribute a rainfall cause.')
            gaps.append('Blockage/capacity allegations require inspection; verified-only topology excludes candidate drainage links.')
        for asset in q.asset_ids:
            self.check();r=GraphQueries(self.repo).run(QueryRequest(template='maintenance_history',id=asset,as_of=self.as_of))
            if r.truncated:gaps.append('Maintenance history capped; missing rows are not absence.')
            for n in r.nodes:
                if n.kind not in {'Inspection','WorkOrder','InterventionOutcome'}:continue
                history.append(n.id)
                date=next((n.properties[k] for k in ('evaluated_at','completed_at','requested_at','created_at') if k in n.properties),None)
                a.history_records.append(HistorySummary(id=n.id,kind=n.kind,occurred_at=date,status=n.properties.get('status'),result=n.properties.get('result')))
            self.paths.extend(r.paths);evs.update(id for p in r.paths for id in p.evidence_ids)
            if q.issue_type=='ROAD_DAMAGE':
                if not any(n.kind=='Inspection' for n in r.nodes):gaps.append('No linked inspection for '+asset+' in bounded history.')
                if not any(n.kind=='WorkOrder' for n in r.nodes):gaps.append('No linked repair/work-order history for '+asset+'.')
                gaps.append('Completed work orders and asset-linked outcomes do not verify resolution of this incident.')
                if not q.details.distress_description:gaps.append('Specific road distress description missing.')
            if q.issue_type=='WASTE_ACCUMULATION' and 'WasteCollectionPoint' in self.asset_labels.get(asset,set()):
                self.check();r=GraphQueries(self.repo).run(QueryRequest(template='ownership_dependencies',id=asset,as_of=self.as_of))
                self.paths.extend(r.paths);evs.update(id for p in r.paths for id in p.evidence_ids)
                if not any(n.kind=='ServiceSchedule' for n in r.nodes):gaps.append('No applicable collection schedule in bounded context.')
                gaps.append('Source pickup local-clock/service-alias warnings retained; schedule adherence is not inferred.')
                after=(timestamp(q.occurred_at)-timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%S.%f')
                at=timestamp(self.as_of).strftime('%Y-%m-%dT%H:%M:%S.%f');key=GraphQueries._time_key
                rows=self.read('MATCH (p:PickupExecution)-[r:PICKUP_FOR]->(a:WasteCollectionPoint {id:$id}) WHERE '+key('p.scheduled_at')+'>=$after AND '+key('p.scheduled_at')+'<=$at RETURN type(r),properties(r),labels(p),properties(p),labels(a),properties(a) ORDER BY '+key('p.scheduled_at')+',p.id,r.id LIMIT $limit',{'id':asset,'after':after,'at':at},100)
                for row in rows:
                    e=self.repo._decode_edge_row(row);n=self.repo.decode_node(row[2],row[3])
                    if not visible(n.properties,self.as_of) or not visible(e.properties,self.as_of):continue
                    ev=self.repo._check_evidence(e.properties)
                    if ev and not visible(ev.properties,self.as_of):continue
                    history.append(n.id)
                    a.history_records.append(HistorySummary(id=n.id,kind=n.kind,occurred_at=n.properties['scheduled_at'],status=n.properties['status']))
                    if n.properties['status']!='MISSED' and not n.properties.get('actual_at'):gaps.append('Pickup '+n.id+' lacks actual execution time; timing remains unknown.')
                    if ev:evs.add(ev.id)
                    if q.details.reported_pickup_status=='MISSED' and n.properties['status']=='COMPLETED':a.contradictions.append('Reported missed collection contrasts with recorded COMPLETED '+n.id+'; source/service timing review required.')
                if not rows:gaps.append('Actual pickup execution records unavailable for this bounded window.')
                if q.details.illegal_dumping_claim is not None:gaps.append('Illegal dumping is a submitted claim; collection failure alone does not verify dumping.')
                if q.details.quantity_description and not names:gaps.append('Quantity text is ambiguous; no numeric waste volume inferred.')
        unique={r.id:r for r in a.history_records}
        a.history_records[:]=sorted(unique.values(),key=lambda r:(timestamp(r.occurred_at) if r.occurred_at else timestamp(self.as_of),r.id))
        a.gaps.extend(dict.fromkeys([*self.gaps,*gaps]));a.history_ids.extend(sorted(set(history)))
        a.source_evidence_ids.extend(sorted(evs));return a
