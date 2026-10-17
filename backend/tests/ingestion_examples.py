"""Synthetic schema test examples only; never municipal history or evaluator facts."""
from app.graph.schema import Registry
from app.ingestion.conversion import ROOT
import json

TIME='2026-09-01T00:00:00Z'
COMPILED='2026-10-17T00:00:00Z'


def source(nodes,edges=()):
    return {'schema_version':2,'fixture_id':'UNIT-SYNTHETIC','nodes':nodes,'relationships':list(edges),'ground_truth_visible_to_agent':False}


def example(kind,id=None):
    r=Registry();p={}
    for f in r.shape(kind)['required']:
        d=r.shape(kind)['properties'][f]
        if f=='municipality_id':continue
        if f=='id':p[f]=id or 'TEST-'+kind
        elif f=='schema_version':p[f]=2
        elif d.get('format')=='date-time':p[f]=TIME
        elif 'enum_ref' in d:p[f]=r.data['enums'][d['enum_ref']][0]
        elif 'enum' in d:p[f]=d['enum'][0]
        elif d['type']=='integer':p[f]=max(1,d.get('minimum',1))
        elif d['type']=='number':p[f]=max(0,d.get('minimum',0))
        elif d['type']=='boolean':p[f]=True
        else:p[f]='Synthetic test value'
    refs=json.loads((ROOT/'contracts/graph_access.json').read_text())['node_references']
    for field,target in refs.get(kind,{}).items():
        if field in p:p[field]='TEST-'+target
    n={'label':kind,'properties':p}
    if kind=='Inspection':n['stage']='HISTORICAL'
    return n


def with_dependencies(nodes):
    policy=json.loads((ROOT/'contracts/graph_access.json').read_text());out={n['properties']['id']:n for n in nodes}
    while True:
        add=[]
        for n in list(out.values()):
            for f,kind in policy['node_references'].get(n['label'],{}).items():
                if f in n['properties'] and n['properties'][f] not in out:add.append(example(kind,n['properties'][f]))
        if not add:return list(out.values())
        out.update({n['properties']['id']:n for n in add})


def complete_source(nodes,edges=()):
    nodes=list(nodes);edges=list(edges)
    for n in list(nodes):
        if n['label']!='PickupExecution':continue
        p=n['properties'];pid=p['id']
        execution=next((e for e in edges if e['type']=='ROUTE_EXECUTION' and e['source_id']==pid),None)
        if execution:p['route_id']=execution['target_id']
        point_edge=next((e for e in edges if e['type']=='PICKUP_FOR' and e['source_id']==pid),None)
        if point_edge:point=point_edge['target_id']
        else:
            point='TEST-POINT-'+pid;nodes.append(example('WasteCollectionPoint',point))
            edges.append({'type':'PICKUP_FOR','source_id':pid,'target_id':point,'properties':{}})
        edges.append({'type':'COLLECTED_BY','source_id':point,'target_id':p['route_id'],'properties':{}})
        if execution is None:edges.append({'type':'ROUTE_EXECUTION','source_id':pid,'target_id':p['route_id'],'properties':{}})
    return source(with_dependencies(nodes),edges)
