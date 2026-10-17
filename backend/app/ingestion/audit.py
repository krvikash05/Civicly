"""Offline-only repository audit. Evaluator payload values never appear in output."""
from collections import Counter, defaultdict
import hashlib
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from app.graph.schema import Registry, timestamp
from app.graph.models import digest
from app.ingestion.conversion import ROOT


def audit_dataset(source):
    r=Registry();nodes=source['nodes'];edges=source['relationships'];by={n['properties']['id']:n for n in nodes};findings=[]
    def issue(code,record,**detail):findings.append({'code':code,'record_id':record,**detail})
    seen=Counter(n['properties']['id'] for n in nodes)
    for id,count in seen.items():
        if count>1:issue('DUPLICATE_NODE_ID',id,count=count)
    for n in nodes:
        p=n['properties'];id=p.get('id');kind=n['label']
        if kind not in r.nodes:issue('UNKNOWN_NODE_TYPE',id);continue
        shape=r.shape(kind)
        for f in set(p)-shape['properties'].keys():issue('UNKNOWN_PROPERTY',id,field=f)
        for f in set(shape['required'])-p.keys():issue('MISSING_CANONICAL_PROPERTY',id,field=f)
        test={**p,'schema_version':3,'municipality_id':'demo-city'}
        if 'value_number' in test:test['value']=test.pop('value_number')
        try:r.validate_node(kind,test)
        except ValueError as error:issue('STRICT_PROPERTY_FAILURE',id,reason=str(error))
        for f,desc in shape['properties'].items():
            if f in p and desc.get('format')=='date-time':
                try:timestamp(p[f])
                except (TypeError,ValueError):issue('INVALID_DATE',id,field=f)
        if 'timezone' in p:
            try:ZoneInfo(p['timezone'])
            except (ZoneInfoNotFoundError,TypeError):issue('INVALID_TIMEZONE',id)
        for f in ('observed_at','started_at','actual_at','recorded_at','completed_at','reported_at'):
            if f in p and p[f]>p.get('created_at',''):issue('EVENT_AFTER_FIXTURE_CREATION',id,field=f)
        if kind=='Evidence' and p.get('reliability')=='VERIFIED' and (not p.get('observed_at') or not p.get('source_record_id')):issue('INCOMPLETE_VERIFIED_EVIDENCE',id)
        if kind=='PickupExecution' and p.get('status')=='MISSED' and 'actual_at' in p:issue('MISSED_WITH_ACTUAL_COMPLETION',id)
    policy=json.loads((ROOT/'contracts/graph_access.json').read_text());groups=defaultdict(list);keys=Counter()
    for i,e in enumerate(edges):
        id=e.get('properties',{}).get('id',f'edge-index:{i}');kind=e['type'];p=e.get('properties',{});s=by.get(e['source_id']);t=by.get(e['target_id'])
        if kind not in r.edges:issue('UNKNOWN_EDGE_TYPE',id);continue
        try:r._properties(r.edges[kind],{**p,'id':id,'municipality_id':'demo-city','created_at':'2026-10-17T00:00:00Z'})
        except ValueError as error:issue('STRICT_EDGE_PROPERTY_FAILURE',id,reason=str(error))
        for f in set(r.edges[kind]['required'])-p.keys():issue('MISSING_EDGE_METADATA',id,field=f)
        for f in p.keys()-r.edges[kind]['properties'].keys():issue('UNKNOWN_EDGE_PROPERTY',id,field=f)
        if s is None or t is None:issue('UNRESOLVED_ENDPOINT',id);continue
        if not set(r.labels(s['label']))&set(r.edges[kind]['from']) or not set(r.labels(t['label']))&set(r.edges[kind]['to']):issue('BAD_DIRECTION_OR_TYPE',id)
        if kind in policy['verified_associations'] and 'association_status' not in p:issue('UNKNOWN_ASSOCIATION_STATUS',id)
        if p.get('source_evidence_id') not in by and 'source_evidence_id' in p:issue('UNRESOLVED_EVIDENCE',id)
        if p.get('association_status')=='VERIFIED':
            ev=by.get(p.get('source_evidence_id'),{}).get('properties',{})
            if not ev.get('observed_at') or not ev.get('source_record_id'):issue('UNSUPPORTED_VERIFICATION_CLAIM',id)
        if kind=='REPORTS' and s['properties']['reported_at']<t['properties']['started_at']:issue('REPORT_PRECEDES_INCIDENT',id)
        keys[(kind,e['source_id'],e['target_id'],p.get('valid_from'),p.get('valid_to'))]+=1
        groups[(kind,e['source_id'])].append(e)
    from app.graph.repository import intersection,interval
    for (kind,id),group in groups.items():
        for i,a in enumerate(group):
            for b in group[i+1:]:
                try:
                    if intersection(interval(a['properties']),interval(b['properties'])) is not None and (a['target_id']==b['target_id'] or kind in policy['singleton_outgoing']):issue('TEMPORAL_CARDINALITY_CONFLICT',id,relationship=kind)
                except ValueError:issue('INVALID_INTERVAL',id,relationship=kind)
    schedule_groups=defaultdict(list)
    for e in edges:
        if e['type']!='HAS_SCHEDULE' or e['target_id'] not in by:continue
        p=by[e['target_id']]['properties']
        try:
            active=intersection(interval(e.get('properties',{})),interval(p))
            if active is None:issue('INAPPLICABLE_SCHEDULE_INTERVAL',e['source_id'])
            else:schedule_groups[(e['source_id'],p['service_type'])].append(active)
        except (ValueError,KeyError):issue('INVALID_SCHEDULE_INTERVAL',e['source_id'])
    for (route,service),spans in schedule_groups.items():
        for i,a in enumerate(spans):
            for b in spans[i+1:]:
                if intersection(a,b) is not None:issue('OVERLAPPING_SAME_SERVICE_SCHEDULE',route,service=service)
    col={e['source_id']:e['target_id'] for e in edges if e['type']=='COLLECTED_BY'};point={e['source_id']:e['target_id'] for e in edges if e['type']=='PICKUP_FOR'}
    for n in nodes:
        id=n['properties']['id']
        for f,kind in policy['node_references'].get(n['label'],{}).items():
            ref=n['properties'].get(f)
            if ref is not None and (ref not in by or kind not in r.labels(by[ref]['label'])):issue('UNRESOLVED_PROPERTY_REFERENCE',id,field=f)
        if n['label']=='PickupExecution' and n['properties']['route_id']!=col.get(point.get(id)):issue('PICKUP_ROUTE_MEMBERSHIP_DISAGREEMENT',id)
    for n in nodes:
        if n['label']!='PickupExecution':continue
        p=n['properties'];route=p['route_id']
        for assignment in groups.get(('HAS_SCHEDULE',route),[]):
            schedule=by.get(assignment['target_id'],{}).get('properties',{})
            clock=re.search(r'\b([0-2][0-9]:[0-5][0-9])\b',schedule.get('schedule_spec',''))
            try:
                actual=timestamp(p['scheduled_at']).astimezone(ZoneInfo(schedule['timezone'])).strftime('%H:%M')
                if clock and actual!=clock.group(1):issue('SCHEDULE_CLOCK_WARNING',p['id'],schedule_id=assignment['target_id'],scheduled_local_clock=actual,source_spec_clock=clock.group(1),classification='Warning only; recurrence/window semantics need domain review')
            except (KeyError,ValueError,ZoneInfoNotFoundError):pass
    counts=Counter(n['label'] for n in nodes)
    return {'source_hash':digest(source),'source_schema_versions':dict(Counter(str(n['properties'].get('schema_version')) for n in nodes)),
            'node_counts':dict(counts),'relationship_counts':dict(Counter(e['type'] for e in edges)),
            'total_nodes':len(nodes),'total_relationships':len(edges),'findings':findings,'finding_counts':dict(Counter(f['code'] for f in findings)),
            'historical_gaps':{'WorkOrder':max(0,20-counts['WorkOrder']),'AgentDecision':max(0,20-counts['AgentDecision']),
                'Inspection':counts['Inspection'],'InterventionOutcome':counts['InterventionOutcome']},
            'unlinked_observation_ids':[id for id,n in by.items() if n['label']=='Observation' and not any(e['source_id']==id or e['target_id']==id for e in edges)],
            'data_sources':[{'id':n['properties']['id'],'origin':n['properties'].get('origin'),'source_uri':n['properties'].get('source_uri'),'explicit_license':None} for n in nodes if n['label']=='DataSource'],
            'stage_inventory':dict(Counter(n.get('stage','HISTORICAL' if n['properties']['id']=='INS-ROAD-PAST' else 'BASELINE_VISIBLE') for n in nodes)),
            'schedule_definitions':[{'id':n['properties']['id'],**{f:n['properties'][f] for f in ('service_type','schedule_spec','recurrence','window_start','window_end','timezone','valid_from','valid_to') if f in n['properties']}} for n in nodes if n['label']=='ServiceSchedule'],
            'service_alias_normalization':'NOT_PERFORMED; naming needs domain review',
            'service_types':dict(Counter(n['properties']['service_type'] for n in nodes if n['label']=='ServiceSchedule'))}


def audit_repository():
    sources={}
    for name in ['contracts/seed_graph.json','contracts/seed_graph_expanded.json']:
        sources[name]=audit_dataset(json.loads((ROOT/name).read_text()))
    manifest=json.loads((ROOT/'data/documents/manifest.json').read_text());docs=[]
    for d in manifest['documents']:
        p=ROOT/d['file_path'];docs.append({'id':d['document_id'],'file_path':d['file_path'],'exists':p.is_file(),
            'hash_matches':p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256'],
            'source_kind':d.get('source_kind'),'version':d.get('version'),'owner_name':d.get('owner_department_name'),
            'missing_owner_id':True,'pdf_available':p.suffix.lower()=='.pdf'})
    excluded={}
    for name in ['contracts/scenarios/catalog.json','contracts/demo_scenarios.json','data/scenarios/hidden_truth.json','data/scenarios/event_reveals.json']:
        data=json.loads((ROOT/name).read_text());excluded[name]={'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),
           'runtime_import':'FORBIDDEN','records':len(data.get('cases',data.get('scenarios',[])))}
    return {'audit_version':1,'registry_hash':Registry().sha256,'sources':sources,'documents':docs,
        'geographic_assets':[str(p.relative_to(ROOT)) for p in (ROOT/'data').rglob('*.geojson')],
        'geometry_gap':'No supplied GeoJSON geometry assets; coordinates are illustrative, not connectivity proof',
        'generator':{'file':'scripts/generate_demo_seed.py','sha256':hashlib.sha256((ROOT/'scripts/generate_demo_seed.py').read_bytes()).hexdigest()},
        'excluded_evaluator_and_stage_sources':excluded}


def scenario_reports(bundle):
    # Offline only: expose IDs/counts/gaps, never titles, expected decisions or reveal text.
    bindings=json.loads((ROOT/'contracts/scenarios/bindings.json').read_text())['bindings']
    catalog=json.loads((ROOT/'contracts/scenarios/catalog.json').read_text())['scenarios']
    reveals=json.loads((ROOT/'data/scenarios/event_reveals.json').read_text())['cases']
    by={n['properties']['id']:n for n in bundle['nodes']};edges=bundle['relationships'];rows=[];releases=[]
    for sc in catalog:
        sid=sc['id'];b=bindings[sid];incs=set(b['incident_ids']);assets=set(b['asset_ids'])
        complaints=[e['source_id'] for e in edges if e['type']=='REPORTS' and e['target_id'] in incs]
        connected=[e['properties']['id'] for e in edges if e['source_id'] in assets and e['type'] in {'DRAINS_TO','UNDERLIES','SERVES','COLLECTED_BY'}]
        rows.append({'scenario_id':sid,'issue_types':sc['issue_types'],'incident_ids':sorted(incs),'complaint_ids':complaints,
            'asset_ids':b['asset_ids'],'cluster_ids':b['cluster_ids'],
            'actual_incident_assets':[e['target_id'] for e in edges if e['type']=='AFFECTS' and e['source_id'] in incs],
            'actual_incident_clusters':[e['target_id'] for e in edges if e['type']=='PART_OF' and e['source_id'] in incs],'missing_bound_ids':sorted((incs|assets|set(b['cluster_ids']))-by.keys()),
            'available_topology_edge_ids':connected,'available_historical_inspections':['INS-ROAD-PAST'] if 'ROAD-R08' in assets else [],
            'available_evidence_ids':sorted({e['properties']['source_evidence_id'] for e in edges if 'source_evidence_id' in e['properties'] and (e['source_id'] in incs|assets|set(complaints)|set(b['cluster_ids']) or e['target_id'] in incs|assets|set(complaints)|set(b['cluster_ids']))}),
            'binding_matches_actual_assets':set(b['asset_ids'])=={e['target_id'] for e in edges if e['type']=='AFFECTS' and e['source_id'] in incs},
            'binding_matches_actual_clusters':set(b['cluster_ids'])=={e['target_id'] for e in edges if e['type']=='PART_OF' and e['source_id'] in incs},
            'unlinked_measurement_count':sum(n['label']=='Observation' and not any(e['source_id']==id or e['target_id']==id for e in edges) for id,n in by.items()),
            'gaps':['Case-specific dated inspections/outcomes not supplied','No historical WorkOrder/AgentDecision chain','Verified physical evidence incomplete'],
            'cross_category_gap':sid=='S07','behavior_status':'NOT_IMPLEMENTED','completion_milestones':['B05','B08-B11','B14','B19-B23']})
        releases.append({'scenario_id':sid,'stage':reveals[sid]['stage'],'payload_sha256':digest(reveals[sid]),
            'restricted_ref':f'data/scenarios/event_reveals.json#/cases/{sid}','initial_graph_import':False})
    return {'schema_version':1,'scenarios':rows,'not_a_behavior_test':True},{'version':1,'releases':releases,'runtime_payloads_included':False}


def input_manifest(source_path,bundle):
    path=Path(source_path).resolve()
    if not path.is_relative_to(ROOT):raise ValueError('Source manifest path must be repository-relative')
    files=['contracts/schema_registry.json','contracts/graph_access.json','contracts/dataset_ingestion.json',
           'contracts/seed_graph.json','contracts/seed_graph_expanded.json','scripts/generate_demo_seed.py',
           'data/documents/manifest.json',str(path.relative_to(ROOT))]
    files+=['backend/app/ingestion/conversion.py']
    return {'version':1,'source_file':str(path.relative_to(ROOT)),'source_kind':'SYNTHETIC',
       'origin':'Repository-authored fictional Civicly Demo City; no real municipality data',
       'license_status':'No explicit per-dataset license supplied; not claimed public licensed data',
       'timezone':'UTC event timestamps; schedule timezone remains source-defined',
       'materialized_at':bundle['conversion_at'],'actual_import_at':'See real import/benchmark report; not inferred from conversion',
       'canonical_source_hash':bundle['source_hash'],'bundle_content_hash':bundle['manifest']['content_hash'],
       'file_sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in dict.fromkeys(files)},
       'document_sha256':{d['file_path']:d['sha256'] for d in json.loads((ROOT/'data/documents/manifest.json').read_text())['documents']}}


def generator_changes(source):
    original=json.loads((ROOT/'contracts/seed_graph_expanded.json').read_text());changes=[]
    for key in ('nodes','relationships'):
        for i,(before,after) in enumerate(zip(original[key],source[key],strict=True)):
            for field in sorted((before.keys()|after.keys())-{'properties'}):
                if before.get(field)!=after.get(field):changes.append({'pointer':f'/{key}/{i}/{field}','before_present':field in before,'before':before.get(field),'after_present':field in after,'after':after.get(field)})
            a=before['properties'];b=after['properties']
            for field in sorted(a.keys()|b.keys()):
                if a.get(field)!=b.get(field) or (field in a)!=(field in b):changes.append({'pointer':f'/{key}/{i}/properties/{field}','before_present':field in a,'before':a.get(field),'after_present':field in b,'after':b.get(field)})
    return {'generator_version':'2.1','classification':'Explicit new synthetic revision, not recovery of historical facts',
       'original_hash':digest(original),'new_source_hash':digest(source),'changes':changes,
       'change_counts':dict(Counter(x['pointer'].split('/')[-1] for x in changes))}
