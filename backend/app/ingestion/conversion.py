"""Deterministic, explicit v1/v2 conversion. No scenario oracle or database access."""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from app.graph.models import digest
from app.graph.schema import Registry, SchemaError, timestamp
from app.graph.repository import interval, intersection

ROOT=Path(__file__).resolve().parents[3]
FORBIDDEN={'hidden_ground_truth','underlying_cause','expected_safe_next_actions','initial_expected_actions',
           'preferred_tool_categories','revealed_observation','evaluation_note','negative_variant','after_evidence'}
INITIAL={'BASELINE_VISIBLE','HISTORICAL'}


class SourceError(ValueError): pass


def reject_answers(value):
    if isinstance(value,dict):
        if FORBIDDEN & value.keys(): raise SourceError('Evaluator/delayed answer fields are forbidden')
        for item in value.values():reject_answers(item)
    elif isinstance(value,list):
        for item in value:reject_answers(item)


def edge_identity(record):
    p=record.get('properties',{})
    return 'REL-'+digest([record['type'],record['source_id'],record['target_id'],p.get('valid_from'),p.get('valid_to')])[:40]


def node_order(nodes,registry,policy):
    pending={n['properties']['id']:n for n in nodes};out=[];done=set()
    while pending:
        ready=[]
        for id,n in pending.items():
            refs=policy['node_references'].get(n['label'],{})
            if all(n['properties'][f] in done for f in refs if f in n['properties']):ready.append(id)
        if not ready:raise SourceError('Unresolved or cyclic node property references')
        for id in sorted(ready):out.append(pending.pop(id));done.add(id)
    return out


def check_graph(nodes,edges,registry=None,*,validate_properties=True):
    """Offline preflight; repository remains authoritative at every actual write."""
    r=registry or Registry();policy=json.loads((ROOT/'contracts/graph_access.json').read_text())
    by={n['properties']['id']:n for n in nodes}
    if len(by)!=len(nodes):raise SourceError('Duplicate node identities')
    if validate_properties:
        for n in nodes:r.validate_node(n['label'],n['properties'])
    for n in nodes:
        for f,kind in policy['node_references'].get(n['label'],{}).items():
            if f in n['properties']:
                ref=by.get(n['properties'][f])
                if ref is None or kind not in r.labels(ref['label']):raise SourceError('Missing or invalid property reference')
    edge_ids=set();groups=defaultdict(list);schedules=defaultdict(list);adj=defaultdict(lambda:defaultdict(set))
    for e in edges:
        p=e['properties'];id=p['id'];s=by.get(e['source_id']);t=by.get(e['target_id']);kind=e['type']
        if id in by or id in edge_ids:raise SourceError('Duplicate global relationship identity')
        edge_ids.add(id)
        if s is None or t is None:raise SourceError('Unresolved endpoints')
        if validate_properties:r.validate_edge(kind,s['label'],s['properties'],t['label'],t['properties'],p)
        if p.get('source_evidence_id'):
            ev=by.get(p['source_evidence_id'])
            if ev is None or ev['label']!='Evidence':raise SourceError('Missing evidence reference')
            ep=ev['properties']
            if p.get('association_status')=='VERIFIED':
                if ep['reliability']!='VERIFIED' or ep['source_kind']=='AGENT' or not ep.get('observed_at') or not ep.get('source_record_id'):raise SourceError('Incomplete verified evidence')
                if any(timestamp(ep[f])>timestamp(p['created_at']) for f in ('observed_at','recorded_at','created_at')):raise SourceError('Future verified evidence')
        group=groups[(kind,e['source_id'])]
        for old in group:
            if intersection(interval(p),interval(old['properties'])) is not None and (old['target_id']==e['target_id'] or kind in policy['singleton_outgoing']):raise SourceError('Temporal cardinality/duplicate conflict')
        group.append(e)
        if kind=='HAS_SCHEDULE':
            span=intersection(interval(p),interval(t['properties']))
            if span is None:raise SourceError('Empty schedule applicability')
            key=(e['source_id'],t['properties']['service_type'])
            if any(intersection(span,v) is not None for v in schedules[key]):raise SourceError('Schedule overlap')
            schedules[key].append(span)
        if kind in {'DEPENDS_ON','DRAINS_TO'}:adj[kind][e['source_id']].add(e['target_id'])
    # No source-controlled inspected-cycle override. Such cycles require separate review.
    for kind,graph in adj.items():
        visiting=set();visited=set()
        def visit(v):
            if v in visiting:raise SourceError('Source network cycle requires explicit domain review')
            if v in visited:return
            visiting.add(v)
            for w in graph.get(v,()):visit(w)
            visiting.remove(v);visited.add(v)
        for v in graph:visit(v)
    return node_order(nodes,r,policy)


def manifest_for(nodes,edges):
    records={n['properties']['id']:digest({'kind':n['label'],'properties':n['properties']}) for n in nodes}
    records.update({e['properties']['id']:digest({'id':e['properties']['id'],'kind':e['type'],'source':e['source_id'],'target':e['target_id'],'properties':e['properties']}) for e in edges})
    return {'nodes':len(nodes),'relationships':len(edges),'node_types':dict(sorted(Counter(n['label'] for n in nodes).items())),
            'relationship_types':dict(sorted(Counter(e['type'] for e in edges).items())),
            'record_hashes':records,'content_hash':digest(records)}


def validate_bundle(bundle):
    if not isinstance(bundle,dict):raise SourceError('Bundle must be an object')
    reject_answers(bundle)
    if set(bundle)!={'contract_version','converter_version','conversion_at','source_hash','registry_hash','nodes','relationships','manifest'}:raise SourceError('Unknown/missing bundle metadata')
    if not isinstance(bundle['nodes'],list) or not isinstance(bundle['relationships'],list):raise SourceError('Bundle records must be arrays')
    for records,keys in ((bundle['nodes'],{'label','properties'}),(bundle['relationships'],{'type','source_id','target_id','properties'})):
        if any(not isinstance(record,dict) or set(record)!=keys or not isinstance(record['properties'],dict) for record in records):raise SourceError('Malformed/unknown compiled record envelope')
    r=Registry()
    if bundle['contract_version']!=1 or bundle['converter_version']!='1.0' or bundle['registry_hash']!=r.sha256:raise SourceError('Unsupported conversion contract/registry')
    timestamp(bundle['conversion_at'])
    if len(bundle['nodes'])+len(bundle['relationships'])>5000:raise SourceError('Import record budget exceeded')
    ordered=check_graph(bundle['nodes'],bundle['relationships'],r)
    if manifest_for(bundle['nodes'],bundle['relationships'])!=bundle['manifest']:raise SourceError('Manifest/content hash mismatch')
    return ordered


def convert(source,conversion_at,*,documents=None):
    timestamp(conversion_at)
    if not isinstance(source,dict):raise SourceError('Source must be an object')
    if not isinstance(source.get('nodes'),list) or not isinstance(source.get('relationships'),list):raise SourceError('Source records must be arrays')
    if len(source['nodes'])+len(source['relationships'])>5000:raise SourceError('Source record budget exceeded')
    if any(not isinstance(n,dict) or not isinstance(n.get('properties'),dict) for n in source['nodes']+source['relationships']):raise SourceError('Malformed source record envelope')
    reject_answers(source)
    if source.get('ground_truth_visible_to_agent') is not False:raise SourceError('Initial source visibility must be explicit and false')
    if set(source)-{'schema_version','fixture_id','description','nodes','relationships','ground_truth_visible_to_agent','generator_version','seed_city'}:raise SourceError('Unknown source envelope properties')
    if type(source.get('schema_version')) is not int or source['schema_version'] not in (1,2,3):raise SourceError('Unsupported source version')
    r=Registry();policy=json.loads((ROOT/'contracts/graph_access.json').read_text());source_hash=digest(source)
    report={'converter_version':'1.0','source_hash':source_hash,'conversion_at':conversion_at,'changes':[],
            'quarantine':[],'provenance':{},'original_counts':{'nodes':len(source['nodes']),'relationships':len(source['relationships'])}}
    receipt='EVD-B04-IMPORT';source_id='SRC-B04-IMPORT'
    def common(id):return {'id':id,'schema_version':3,'municipality_id':'demo-city','created_at':conversion_at,'updated_at':conversion_at}
    def rejected(pointer,record,reason):
        original=source['nodes'][int(pointer.split('/')[-1])] if pointer.startswith('/nodes/') else record
        report['quarantine'].append({'pointer':pointer,'record':original,'reason':reason})
    def changes(pointer,before,after,reason):
        for f in sorted(set(before)|set(after)):
            if before.get(f)!=after.get(f) or (f in before)!=(f in after):report['changes'].append({'pointer':pointer,'field':f,'before_present':f in before,'before':before.get(f),'after_present':f in after,'after':after.get(f),'rule':({'schema_version':'LEGACY_TO_V3','municipality_id':'FIXED_DEMO_SCOPE','created_at':'MATERIALIZATION_NOT_EVENT_TIME','updated_at':'MATERIALIZATION_NOT_EVENT_TIME','latitude':'VERIFIED_COORDINATE_WIRE_PRECISION','longitude':'VERIFIED_COORDINATE_WIRE_PRECISION','value_number':'LOSSLESS_NUMERIC_RENAME','value':'LOSSLESS_NUMERIC_RENAME','source_record_id':'SOURCE_JSON_POINTER','id':'DETERMINISTIC_EDGE_ID','source_evidence_id':'IMPORT_RECEIPT_OR_ORIGINAL_EVIDENCE','reliability':'UNSUPPORTED_VERIFICATION_DOWNGRADE','association_status':'EXPLICIT_UNKNOWN_OR_UNSUPPORTED_VERIFICATION'}.get(f,reason))})
    counts=Counter(n.get('properties',{}).get('id') for n in source['nodes']);nodes=[]
    for i,raw in enumerate(source['nodes']):
        ptr=f'/nodes/{i}';original=raw.get('properties',{});p=deepcopy(original);kind=raw.get('label')
        try:
            if set(raw)-{'label','properties','stage'}:raise SourceError('Unknown node envelope fields')
            if raw.get('stage','HISTORICAL' if p.get('id')=='INS-ROAD-PAST' else 'BASELINE_VISIBLE') not in INITIAL:raise SourceError('NON_INITIAL_STAGE')
            if kind=='Inspection' and p.get('id')!='INS-ROAD-PAST' and raw.get('stage')!='HISTORICAL':raise SourceError('UNDECLARED_INSPECTION_STAGE')
            if kind not in r.nodes or type(p.get('schema_version')) is not int or p.get('schema_version') not in (1,2,3):raise SourceError('Unsupported node type/version')
            if counts[p.get('id')]!=1 or p.get('id') in {receipt,source_id}:raise SourceError('Duplicate/reserved node ID')
            if 'municipality_id' in p and p['municipality_id']!='demo-city':raise SourceError('Invalid source municipality')
            if p.get('source_kind','SYNTHETIC')!='SYNTHETIC':raise SourceError('Unsupported non-synthetic source profile')
            if kind=='Observation' and 'value_number' in p:
                if 'value' in p:raise SourceError('Ambiguous numeric fields')
                p['value']=p.pop('value_number')
            for field,value in list(p.items()):
                if type(value) is float and float(format(value,'.15g'))!=value:
                    if field in ('latitude','longitude'):p[field]=float(format(value,'.15g'))
                    else:raise SourceError('UNSUPPORTED_NUMERIC_WIRE_PRECISION:'+field)
            if kind=='PickupExecution' and p.get('status')=='MISSED' and 'actual_at' in p:raise SourceError('MISSED_WITH_ACTUAL_COMPLETION')
            if any(timestamp(p[f])>timestamp(conversion_at) for f in ('observed_at','recorded_at','completed_at','actual_at','started_at','reported_at') if f in p):raise SourceError('FUTURE_STAGE_DATE')
            r.validate_node(kind,{**p,'schema_version':3,'municipality_id':'demo-city'})
            p.update(schema_version=3,municipality_id='demo-city',created_at=conversion_at)
            if 'updated_at' in r.shape(kind)['properties']:p['updated_at']=conversion_at
            if kind=='Evidence':
                p.setdefault('source_record_id',f'sha256:{source_hash}#{ptr}')
                if p.get('reliability')=='VERIFIED' and not p.get('observed_at'):p['reliability']='UNVERIFIED'
            r.validate_node(kind,p)
            nodes.append({'label':kind,'properties':p})
            report['provenance'][p['id']]={'source_hash':source_hash,'pointer':ptr,'stage':raw.get('stage','BASELINE_VISIBLE')}
            changes(ptr,original,p,'NUMERIC_FIELD_RENAME_OR_UNSUPPORTED_VERIFICATION')
        except (ValueError,TypeError,KeyError) as error:rejected(ptr,raw,str(error))
    # Source route records must agree with explicit point/route membership, never proximity.
    collected={e['source_id']:e['target_id'] for e in source['relationships'] if e['type']=='COLLECTED_BY'}
    points={e['source_id']:e['target_id'] for e in source['relationships'] if e['type']=='PICKUP_FOR'}
    invalid=set()
    for n in nodes:
        p=n['properties'];id=p['id']
        if n['label']=='PickupExecution' and (id not in points or p['route_id']!=collected.get(points[id])):
            invalid.add(id);rejected(report['provenance'][id]['pointer'],n,'PICKUP_ROUTE_MEMBERSHIP_DISAGREEMENT')
    by={n['properties']['id']:n for n in nodes if n['properties']['id'] not in invalid}
    while True:
        bad=[]
        for id,n in by.items():
            for f,kind in policy['node_references'].get(n['label'],{}).items():
                if f in n['properties'] and (n['properties'][f] not in by or kind not in r.labels(by[n['properties'][f]]['label'])):bad.append(id);break
        if not bad:break
        for id in bad:rejected(report['provenance'][id]['pointer'],by.pop(id),'UNRESOLVED_PROPERTY_REFERENCE')
    by[source_id]={'label':'DataSource','properties':{**common(source_id),'name':'Synthetic fixture import source','source_type':'SYNTHETIC_FIXTURE','source_kind':'SYNTHETIC','origin':'Civicly explicit B04 conversion','source_uri':f'sha256:{source_hash}'}}
    by[receipt]={'label':'Evidence','properties':{**common(receipt),'evidence_type':'IMPORT_RECEIPT','summary':'Synthetic source import receipt; no physical verification asserted','reliability':'UNVERIFIED','recorded_at':conversion_at,'source_kind':'SYNTHETIC','basis':'REPORTED','source_record_id':f'sha256:{source_hash}'}}
    if documents is not None:
        for record in documents['documents']:
            path=(ROOT/record['file_path']).resolve()
            if not path.is_relative_to((ROOT/'data/documents').resolve()):raise SourceError('Document path outside approved source directory')
            if not record.get('synthetic') or record.get('source_kind')!='SYNTHETIC' or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=record['sha256']:raise SourceError('Unverified document manifest')
            id=record['document_id']
            if id in by:raise SourceError('Document identity collision')
            by[id]={'label':'Document','properties':{**common(id),'title':record['title'],'document_type':'SYNTHETIC_MUNICIPAL_DOCUMENT','content_ref':record['file_path'],'content_hash':record['sha256'],'source_uri':record['file_path']}}
            report['provenance'][id]={'source_hash':digest(record),'pointer':record['file_path'],'stage':'BASELINE_VISIBLE'}
    edges=[];seen=set()
    for i,raw in enumerate(source['relationships']):
        ptr=f'/relationships/{i}';p=deepcopy(raw.get('properties',{}));original=deepcopy(p)
        try:
            if set(raw)-{'type','source_id','target_id','properties','stage'}:raise SourceError('Unknown edge envelope fields')
            if raw.get('stage','BASELINE_VISIBLE') not in INITIAL:raise SourceError('NON_INITIAL_STAGE')
            s=by.get(raw['source_id']);t=by.get(raw['target_id'])
            if s is None or t is None:raise SourceError('UNRESOLVED_ENDPOINT')
            if raw['type']=='REPORTS' and timestamp(s['properties']['reported_at'])<timestamp(t['properties']['started_at']):raise SourceError('REPORT_PRECEDES_INCIDENT')
            if 'municipality_id' in p and p['municipality_id']!='demo-city':raise SourceError('Invalid edge municipality')
            p.update(id=edge_identity(raw),municipality_id='demo-city',created_at=conversion_at)
            p.setdefault('source_evidence_id',receipt)
            if raw['type'] in policy['verified_associations']:
                p.setdefault('association_status','CANDIDATE')
                ev=by.get(p['source_evidence_id'],{}).get('properties',{})
                if p['association_status']=='VERIFIED' and (ev.get('reliability')!='VERIFIED' or not ev.get('observed_at')):p['association_status']='CANDIDATE'
            if p['id'] in seen:raise SourceError('DUPLICATE_RELATIONSHIP_IDENTITY')
            if p['source_evidence_id'] not in by or by[p['source_evidence_id']]['label']!='Evidence':raise SourceError('UNRESOLVED_EVIDENCE_REFERENCE')
            r.validate_edge(raw['type'],s['label'],s['properties'],t['label'],t['properties'],p)
            e={'type':raw['type'],'source_id':raw['source_id'],'target_id':raw['target_id'],'properties':p}
            # All policy conflicts are explicit quarantine, no silent last-write-wins.
            check_graph(list(by.values()),edges+[e],r,validate_properties=False)
            edges.append(e);seen.add(p['id'])
            changes(ptr,original,p,'STABLE_ID_PROVENANCE_OR_UNSUPPORTED_VERIFICATION')
            report['provenance'][p['id']]={'source_hash':source_hash,'pointer':ptr,'stage':raw.get('stage','BASELINE_VISIBLE')}
        except (ValueError,TypeError,KeyError) as error:rejected(ptr,raw,str(error))
    extra={'type':'DERIVED_FROM','source_id':receipt,'target_id':source_id,'properties':{'id':'REL-B04-RECEIPT-SOURCE','municipality_id':'demo-city','created_at':conversion_at}}
    edges.append(extra)
    nodes=check_graph(list(by.values()),edges,r)
    bundle={'contract_version':1,'converter_version':'1.0','conversion_at':conversion_at,'source_hash':source_hash,'registry_hash':r.sha256,'nodes':nodes,'relationships':edges,'manifest':manifest_for(nodes,edges)}
    report['converted_manifest']=bundle['manifest'];validate_bundle(bundle)
    return bundle,report
