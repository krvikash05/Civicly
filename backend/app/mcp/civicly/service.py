"""Read-oriented service adapters; graph reasoning remains in accepted B03/B05."""
from datetime import timedelta
import json
from app.graph.repository import GraphRepository,NotFound
from app.graph.queries import GraphQueries
from app.graph.models import QueryRequest,NodeRecord,EdgeRecord
from app.graph.analysis.engine import GraphAnalysis
from app.graph.analysis.models import AnalysisRequest,CaseRequest
from app.graph.schema import timestamp,utc_now
from app.mcp.runtime import CITY_GRAPH
from .contracts import READ,PAYLOADS,SERVER,SCHEMA_VERSION,INVENTORY_HASH,validate,digest
from .storage import ScopedClient

UNAVAILABLE={'retrieve_case_memory':'B10 persistent memory not implemented; no synthetic history substituted',
 'get_organizational_procedures':'B11 sourced GraphRAG/versioned procedures not implemented',
 'get_source_document_excerpt':'B11 versioned source retrieval unavailable; filesystem/evaluator access denied',
 'get_monitoring_status':'B14/B15 monitoring lifecycle not implemented; no invented operational state'}


def visible(props,as_of):
    at=timestamp(as_of)
    return all(timestamp(props[k])<=at for k in ('created_at','updated_at','observed_at','recorded_at','requested_at','actual_at','decided_at') if k in props) and ('valid_from' not in props or timestamp(props['valid_from'])<=at) and ('valid_to' not in props or at<timestamp(props['valid_to']))


class CivicReadService:
    def __init__(self,client):
        self.repo=GraphRepository(ScopedClient(client,CITY_GRAPH),CITY_GRAPH)
        self.analysis=GraphAnalysis(self.repo)
    def revision(self):
        row=self.repo._read("MATCH (m:CivicSchemaMigration {id:$id}) WHERE m.state='READY' RETURN coalesce(m.repo_revision,0),coalesce(m.repo_pending,'') LIMIT 1",{'id':'0001'})
        if len(row)!=1 or row[0][1]:raise ValueError('Pending/unready source')
        return row[0][0]
    def result(self,name,ctx,as_of):
        payload={} if PAYLOADS[name] in {'document_excerpt','monitoring'} else '' if PAYLOADS[name]=='work_order_status' else []
        r={'status':'SUCCESS','trace_id':ctx.trace_id,'execution_id':ctx.execution_id,'context':ctx.model_dump(mode='json'),
           'server_id':SERVER,'tool_name':name,'schema_version':SCHEMA_VERSION,'inventory_version':INVENTORY_HASH,
           'source_evidence_ids':[],'simulation_mode':True,'graph_revision':None,'truncated':False,'search_limited':True,'error':None,
           PAYLOADS[name]:payload,'data':{'nodes':[],'edges':[],'paths':[],'gaps':[],'reservations':[], 'as_of':as_of}}
        if name=='get_work_order_status':
            r.update(blocking_task_ids=[],latest_status_event_ids=[])
            r['data']['gaps'].append('blocking_task_ids and latest_status_event_ids retrieval unavailable until B12–B15; empty lists are unknown, not verified empty operational relationships')
        return r
    def run(self,name,args,ctx):
        as_of=args.get('as_of',utc_now());timestamp(as_of);r=self.result(name,ctx,as_of);before=self.revision();r['graph_revision']=before
        if name in UNAVAILABLE:
            r['status']='UNAVAILABLE';r['data']['gaps']=[UNAVAILABLE[name]]
        elif name=='find_related_incidents':
            result=self.analysis.cases(CaseRequest(as_of=as_of,seed_incident_id=args['incident_id'],limit=args['max_results'],include_candidates=args.get('include_candidates',False)))
            self.project(r,result)
            r['related_incidents']=[{'incident_id':row.id,'relationship_reason':json.dumps(row.factors,sort_keys=True),
                'evidence_ids':sorted({ev for p in result.paths if p.id in row.path_ids for ev in p.evidence_ids})} for row in result.rows]
        elif name=='trace_infrastructure_dependencies':
            self.repo.get_node(args['asset_id'],'InfrastructureAsset')
            # investigation_id is correlation context, not a fabricated investigation record.
            directions=['downstream','upstream'] if args['direction']=='BOTH' else [args['direction'].lower()]
            for direction in directions:
                operation='dependencies' if args.get('network')=='TYPED_DEPENDENCIES' else 'reachability'
                result=self.analysis.run(AnalysisRequest(operation=operation,ids=(args['asset_id'],),as_of=as_of,direction=direction,max_hops=args['max_hops'],include_candidates=args.get('include_candidates',False)))
                self.project(r,result,merge=True)
            for path in r['data']['paths']:
                edges={e['id']:e for e in r['data']['edges']};statuses=[edges[e]['properties'].get('association_status') for e in path['edge_ids']]
                if not statuses:continue
                status='VERIFIED' if all(s=='VERIFIED' for s in statuses) else 'CANDIDATE' if 'CANDIDATE' in statuses else 'REPORTED'
                assets={n['id'] for n in r['data']['nodes'] if 'InfrastructureAsset' in n['labels']}
                kinds=[edges[e]['kind'] for e in path['edge_ids']]
                r['paths'].append({'asset_ids':[id for id in path['node_ids'] if id in assets],'relationship':'/'.join(kinds),'verification_status':status,'source_evidence_ids':path['evidence_ids']})
        elif name=='get_maintenance_history':
            if timestamp(args['from_time'])>timestamp(args['to_time']) or timestamp(args['to_time'])>timestamp(as_of):raise ValueError('Invalid history interval')
            result=GraphQueries(self.repo).run(QueryRequest(template='maintenance_history',id=args['asset_id'],as_of=args['to_time'],after=args['from_time'],include_candidates=args.get('include_candidates',False)))
            self.project(r,result)
            for n in result.nodes:
                if n.kind not in {'Inspection','WorkOrder','InterventionOutcome'}:continue
                date=next((n.properties[k] for k in ['observed_at','completed_at','requested_at','created_at'] if k in n.properties),None)
                if date and timestamp(args['from_time'])<=timestamp(date)<=timestamp(args['to_time']):
                    r['records'].append({'record_id':n.id,'event_type':n.kind,'occurred_at':date,'evidence_ids':self.maintenance_evidence(result,n)})
            r['data']['gaps'].append('Asset-linked history is contextual; absent repair/decision chains are not proof of resolution')
        elif name in {'get_pickup_execution_history','get_road_condition_history'}:
            pickup=name=='get_pickup_execution_history';root=args['collection_point_id' if pickup else 'road_segment_id']
            self.repo.get_node(root,'WasteCollectionPoint' if pickup else 'RoadSegment')
            after=timestamp(as_of)-timedelta(days=args.get('days',30))
            # WHERE/ORDER BY precede the100+1 cap in the actual RO query, including
            # source evidence visibility. UTC normalization reuses accepted B03.
            rows=self.repo._read(self.history_query(pickup),{'id':root,'scope':'demo-city',
                'as_of':timestamp(as_of).strftime('%Y-%m-%dT%H:%M:%S.%f'),
                'after':after.strftime('%Y-%m-%dT%H:%M:%S.%f')})
            r['truncated']=len(rows)>100
            r['data']['reservations'].append('History window inclusive; chronological UTC ascending, stable event ID then relationship ID;100 records plus one lookahead, before export graph caps. Truncation is not absence.')
            for labels,props,kind,ep,al,ap in rows[:100]:
                n=self.repo.decode_node(labels,props);a=self.repo.decode_node(al,ap);e=self.repo._decode_edge_row([kind,ep,labels,props,al,ap])
                # No schedule clock reinterpretation or guessed dates.
                date=props['scheduled_at' if pickup else 'observed_at']
                if visible(props,as_of) and visible(ep,as_of) and visible(ap,as_of) and after<=timestamp(date)<=timestamp(as_of):
                    evidence_ids=sorted({v for v in (ep.get('source_evidence_id'),props.get('evidence_id')) if v})
                    evidence=[self.repo.get_node(id,'Evidence') for id in evidence_ids]
                    if any(not visible(v.properties,as_of) for v in evidence):raise ValueError('Future evidence excluded')
                    existing={v['id'] for v in r['data']['nodes']}
                    if len(existing|{v.id for v in [n,a,*evidence]})>120 or len(r['data']['edges'])>=200:
                        r['truncated']=True;break
                    self.add_records(r,[n,a,*evidence],[e],[])
                    r['source_evidence_ids'].extend(evidence_ids)
                    r[PAYLOADS[name]].append({'id':n.id,'properties':n.properties})
            if pickup:r['data']['gaps'].append('Source pickup local-clock/service alias warnings remain; no schedule reinterpretation')
        elif name=='get_work_order_status':
            node=self.repo.get_node(args['work_order_id'],'WorkOrder')
            if not visible(node.properties,as_of):raise NotFound('Work order outside time')
            self.add_records(r,[node],[],[]);r['work_order_status']=node.properties['status']
            r['data']['gaps'].append('Status is recorded graph state; no workflow execution or inferred completion')
        elif name=='get_decision_evidence_path':
            node=self.repo.get_node(args['decision_id'],'AgentDecision')
            if not visible(node.properties,as_of):raise NotFound('Decision outside time')
            rows=self.repo._read('MATCH (d:AgentDecision {id:$id})-[e:JUSTIFIED_BY]->(v:CivicEntity) RETURN labels(v),properties(v),type(e),properties(e) LIMIT 101',{'id':node.id})
            r['truncated']=len(rows)>100;self.add_records(r,[node],[],[])
            for labels,props,kind,ep in rows[:100]:
                target=self.repo.decode_node(labels,props);e=self.repo._decode_edge_row([kind,ep,self.repo.registry.labels(node.kind),node.properties,labels,props])
                if visible(props,as_of) and visible(ep,as_of):
                    path={'id':digest([node.id,e.id,target.id]),'node_ids':[node.id,target.id],'edge_ids':[e.id],'directions':['OUTGOING'],'evidence_ids':[target.id] if target.kind=='Evidence' else [],'context':{}}
                    self.add_records(r,[target],[e],[path]);r['graph_paths'].append(path)
                    if ep.get('source_evidence_id'):self.evidence(r,ep['source_evidence_id'],as_of)
                    if target.kind=='Evidence':self.evidence(r,target.id,as_of)
            r['data']['gaps'].append('Only direct recorded JUSTIFIED_BY evidence is retrieved; no agent decision fabricated')
        elif name=='retrieve_external_evidence':
            # No normative Observation->Location relation exists. Do not guess associations
            # or return the55 unlinked observations as location-specific evidence.
            self.repo.get_node(args['location_id'],'Location')
            if timestamp(args['from_time'])>timestamp(args['to_time']) or timestamp(args['to_time'])>timestamp(as_of):raise ValueError('Invalid observation interval')
            r['status']='UNAVAILABLE';r['data']['gaps']=['No registered source-backed location association for the unlinked Observations; no external provider in B07']
        else:raise ValueError('No read handler')
        if not r[PAYLOADS[name]] and r['status']=='SUCCESS':r['data']['gaps'].append('No matching recorded results within this bounded query; not proof of global absence')
        if self.revision()!=before:raise ValueError('Source revision changed')
        r['source_evidence_ids']=sorted(set(r['source_evidence_ids']))
        if r['status']=='SUCCESS' and (r['truncated'] or r['search_limited'] or r['data']['gaps']):r['status']='PARTIAL'
        if not r[PAYLOADS[name]] and not r['data']['nodes'] and r['status']=='SUCCESS':r['status']='UNAVAILABLE'
        if r['status']=='UNAVAILABLE':r['error']={'code':'DATA_UNAVAILABLE','message':'Required sourced data or designated capability is unavailable','retryable':False}
        validate(READ[name]['output_schema'],r);return r
    @staticmethod
    def maintenance_evidence(result,event):
        """Evidence on the event's own validated prefix; PRODUCED extends inspections.

        A WorkOrder prefix does not inherit evidence from a later outcome merely
        because both occur on an exported path. Response-wide union stays separate.
        """
        nodes={n.id:n for n in result.nodes};edges={e.id:e for e in result.edges};ids=set()
        for path in result.paths:
            if event.id not in path.node_ids:continue
            end=path.node_ids.index(event.id)
            if (event.kind=='Inspection' and end<len(path.edge_ids)
                and edges[path.edge_ids[end]].kind=='PRODUCED'
                and nodes[path.node_ids[end+1]].kind=='Evidence'):
                end+=1
            ids.update(nodes[id].id for id in path.node_ids[:end+1] if nodes[id].kind=='Evidence')
            ids.update(edges[id].properties['source_evidence_id'] for id in path.edge_ids[:end]
                       if edges[id].properties.get('source_evidence_id'))
        return sorted(ids)

    @staticmethod
    def history_query(pickup):
        """Two fixed bounded templates; no identifiers or query text from callers."""
        label,relation,date=('PickupExecution','PICKUP_FOR','scheduled_at') if pickup else ('AssetConditionSnapshot','CONDITION_OF','observed_at')
        key=GraphQueries._time_key
        def visibility(var):
            fields=('created_at','updated_at','observed_at','recorded_at','requested_at','actual_at','decided_at')
            checks=[f'({var}.{field} IS NULL OR {key(var+"."+field)}<=$as_of)' for field in fields]
            checks += [f'({var}.valid_from IS NULL OR {key(var+".valid_from")}<=$as_of)',
                       f'({var}.valid_to IS NULL OR $as_of<{key(var+".valid_to")})']
            return ' AND '.join(checks)
        checks=[f'{var}.municipality_id=$scope AND '+visibility(var) for var in ('n','e','a')]
        checks += [f'(n.evidence_id IS NULL OR (ne IS NOT NULL AND {visibility("ne")}))',
                   f'(e.source_evidence_id IS NULL OR (ee IS NOT NULL AND {visibility("ee")}))',
                   f'$after<={key("n."+date)} AND {key("n."+date)}<=$as_of']
        return (f'MATCH (n:{label})-[e:{relation}]->(a:CivicEntity {{id:$id,municipality_id:$scope}}) '
                'OPTIONAL MATCH (ne:Evidence {id:n.evidence_id,municipality_id:$scope}) '
                'OPTIONAL MATCH (ee:Evidence {id:e.source_evidence_id,municipality_id:$scope}) '
                'WITH n,e,a,ne,ee WHERE '+' AND '.join(checks)+
                f' WITH n,e,a,{key("n."+date)} AS event_time ORDER BY event_time ASC,n.id ASC,e.id ASC LIMIT 101 '
                'RETURN labels(n),properties(n),type(e),properties(e),labels(a),properties(a)')

    def evidence(self,r,id,as_of):
        node=self.repo.get_node(id,'Evidence')
        if not visible(node.properties,as_of):raise ValueError('Future evidence excluded')
        self.add_records(r,[node],[],[])
        if id not in r['source_evidence_ids']:r['source_evidence_ids'].append(id)
    def add_records(self,r,nodes,edges,paths):
        d=r['data']
        for key,values in [('nodes',nodes),('edges',edges),('paths',paths)]:
            merged={v['id']:v for v in d[key]}
            for value in values:
                value=value.model_dump(mode='json') if hasattr(value,'model_dump') else value
                if key=='paths' and 'id' not in value:value={'id':digest(value),**value}
                merged[value['id']]=value
            cap={'nodes':120,'edges':200,'paths':100}[key]
            if len(merged)>cap:r['truncated']=True
            d[key]=list(merged.values())[:cap]
        # No orphan proof references after merged BOTH-direction export caps.
        ni={n['id'] for n in d['nodes']};ei={e['id'] for e in d['edges']}
        d['edges']=[e for e in d['edges'] if e['source'] in ni and e['target'] in ni]
        ei={e['id'] for e in d['edges']}
        d['paths']=[p for p in d['paths'] if set(p['node_ids'])<=ni and set(p['edge_ids'])<=ei]
    def project(self,r,result,merge=False):
        self.add_records(r,result.nodes,result.edges,[p.model_dump(mode='json') for p in result.paths])
        r['truncated']|=result.truncated;r['search_limited']=result.search_limited
        r['data']['reservations']=list(dict.fromkeys(r['data']['reservations']+list(result.reservations)))
        r['data']['gaps']=list(dict.fromkeys(r['data']['gaps']+list(getattr(result,'gaps',()))))
        for p in result.paths:
            for id in p.evidence_ids:self.evidence(r,id,r['data']['as_of'])
