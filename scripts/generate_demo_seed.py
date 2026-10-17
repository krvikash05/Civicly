#!/usr/bin/env python3
"""Build a deterministic, fully agent-visible synthetic city graph.

IMPORTANT: No hidden causal answers / future inspection results are put here.
This script generates demonstration *data fixtures*, not Civicly's running backend.
"""
import json
import pathlib
import collections
from datetime import datetime,timedelta,timezone

ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=json.loads((ROOT/'contracts/seed_graph.json').read_text())
REG=json.loads((ROOT/'contracts/schema_registry.json').read_text())
NODES=BASE['nodes'].copy(); EDGES=BASE['relationships'].copy()
NODE_IDS={n['properties']['id'] for n in NODES}
EDGE_KEYS={(r['type'],r['source_id'],r['target_id']) for r in EDGES}
START=datetime(2026,6,1,0,0,tzinfo=timezone.utc)
def iso(offset_days=0,hours=0): return (START+timedelta(days=offset_days,hours=hours)).strftime('%Y-%m-%dT%H:%M:%SZ')
def add(label,id,**props):
    if id in NODE_IDS: return id
    shape=REG['node_types'][label]
    d={'id':id,'schema_version':2,'created_at':iso(),'updated_at':iso(),**props}
    miss=set(shape['required'])-d.keys()
    if miss: raise ValueError(f'{label} {id}: missing {miss}')
    NODES.append({'label':label,'properties':d});NODE_IDS.add(id)
    return id

def edge(t,s,d,**props):
    if s not in NODE_IDS or d not in NODE_IDS: raise ValueError(f'unknown edge endpoints {t} {s} -> {d}')
    k=(t,s,d)
    if k not in EDGE_KEYS: EDGES.append({'type':t,'source_id':s,'target_id':d,'properties':props});EDGE_KEYS.add(k)

# fictional wards and map locations; coordinates are purely illustrative
zones=['ZONE-07']+[add('Zone',f'ZONE-{z:02d}',name=f'Demo Ward {z:02d}',zone_type='WARD') for z in range(8,12)]
locations=['LOC-JUNCTION','LOC-MARKET','LOC-ROAD','LOC-OUTFALL']
for i in range(4,50):
  z=zones[(i//10)%5]
  lid=add('Location',f'LOC-{i:03d}',name=f'Fictional Site {i:03d}',latitude=25.305+((i*13)%40)*0.0003,longitude=82.96+((i*17)%40)*0.0003)
  edge('IN_ZONE',lid,z)
  locations.append(lid)

# drainage topology: separate catchments with explicit verified flow chains, no nearest-neighbor edges
all_drains=['DRAIN-D12','DRAIN-D18']
for ward in range(5):
  prev=None
  for j in range(8):
    k=ward*8+j
    did=add('DrainSegment',f'DRAIN-{k+100:03d}',name=f'Demo storm drain {k+100}',asset_type='DRAIN_SEGMENT',operational_status='ACTIVE',condition='UNKNOWN',design_capacity=0.7+(k%4)*.15,capacity_unit='m3_per_second')
    edge('LOCATED_AT',did,locations[(k+5)%len(locations)])
    edge('MAINTAINED_BY',did,'DEPT-DRAIN')
    if prev: edge('DRAINS_TO',prev,did,association_status='VERIFIED',source_evidence_id='EVD-ASSET-LIST')
    prev=did;all_drains.append(did)
  inlet=add('DrainInlet',f'INLET-{ward+20:03d}',name=f'Demo inlet {ward}',asset_type='DRAIN_INLET',operational_status='ACTIVE',condition='UNKNOWN')
  edge('LOCATED_AT',inlet,locations[(ward*9+8)%len(locations)])
  edge('MAINTAINED_BY',inlet,'DEPT-DRAIN')
  edge('DRAINS_TO',inlet,f'DRAIN-{ward*8+100:03d}',association_status='VERIFIED',source_evidence_id='EVD-ASSET-LIST')
  add('DrainageCatchment',f'CATCH-{ward+1:02d}',name=f'Demo catchment {ward+1}',catchment_type='STORMWATER',area_m2=30000+ward*5000)
  edge('DRAINS_CATCHMENT',f'CATCH-{ward+1:02d}',inlet)
  edge('DRAINS_CATCHMENT',f'CATCH-{ward+1:02d}',f'DRAIN-{ward*8+100:03d}')

roads=['ROAD-R08']
for i in range(35):
  id=add('RoadSegment',f'ROAD-{i+100:03d}',name=f'Demo road segment {i+100}',asset_type='ROAD_SEGMENT',operational_status='ACTIVE',surface_type='ASPHALT',condition='SURVEY_PENDING')
  roads.append(id);edge('LOCATED_AT',id,locations[i%len(locations)]);edge('MAINTAINED_BY',id,'DEPT-ROAD')
pipes=['PIPE-P02']
for i in range(16):
  id=add('WaterPipe',f'PIPE-{i+100:03d}',name=f'Demo utility pipe {i+100}',asset_type='WATER_PIPE',operational_status='ACTIVE',condition='UNKNOWN')
  pipes.append(id);edge('LOCATED_AT',id,locations[(i*2)%len(locations)]);edge('MAINTAINED_BY',id,'DEPT-WATER')
  edge('UNDERLIES',id,roads[(i+3)%len(roads)],association_status='VERIFIED',source_evidence_id='EVD-ASSET-LIST')

routes=['ROUTE-C03'];waste=['WASTE-W03']
for j in range(1,11):
  route=add('CollectionRoute',f'ROUTE-{j+100:03d}',route_code=f'ROUTE-{j+100:03d}',operational_status='ACTIVE');routes.append(route)
  sch=add('ServiceSchedule',f'SCH-{j+100:03d}',schedule_spec='MON,WED,FRI@07:00',service_type='WASTE_COLLECTION',timezone='Asia/Kolkata',valid_from=iso())
  edge('HAS_SCHEDULE',route,sch)
for i in range(24):
  id=add('WasteCollectionPoint',f'WASTE-{i+100:03d}',name=f'Demo waste point {i+100}',asset_type='WASTE_COLLECTION_POINT',operational_status='ACTIVE',capacity_liters=350+(i%3)*200,collection_type='BIN')
  waste.append(id);edge('LOCATED_AT',id,locations[(i*2+1)%len(locations)]);edge('MAINTAINED_BY',id,'DEPT-SAN');edge('COLLECTED_BY',id,routes[(i%len(routes))])

# measured observations and actual/missed collection records - not a hidden cause label
src='SRC-MUNI-SEED'
for i in range(110):
  target=waste[i%len(waste)]
  route=routes[i%len(routes)]
  state='MISSED' if i in (3,8,14,20,29,52,72,86) else ('PARTIAL' if i in (32,62,91) else 'COMPLETED')
  ex=add('PickupExecution',f'PICK-{i+1:04d}',route_id=route,scheduled_at=iso(i%90,hours=7),status=state,actual_at=iso(i%90,hours=8) if state!='MISSED' else iso(i%90,hours=7),source_record_id=f'DEMO_PICK_{i+1:04d}')
  edge('PICKUP_FOR',ex,target);edge('ROUTE_EXECUTION',ex,route)

for i in range(30):
  ev=add('RainfallEvent',f'RAIN-{i+1:03d}',started_at=iso(i*3,hours=4),duration_minutes=90+(i%3)*30,total_mm=13+(i%7)*7,source_record_id=f'DEMO_RAIN_{i+1:03d}',zone_id=zones[i%len(zones)])
  edge('RAINFALL_AFFECTS',ev,zones[i%len(zones)])

# recurring clusters and canonical distinct incidents, variable complaint fan-out
clusters=['CLUSTER-FLOOD','CLUSTER-ROAD','CLUSTER-WASTE']
issue_cycle=['WATERLOGGING','ROAD_DAMAGE','WASTE_ACCUMULATION']
for i in range(3,22):
 issue=issue_cycle[i%3]; c=add('ProblemCluster',f'CLUSTER-{i+1:03d}',title=f'Demo recurring {issue.lower()} cluster {i+1}',pattern_type='RECURRENT',status='OPEN',first_seen_at=iso(i*3))
 clusters.append(c)
incidents=['INC-FLOOD-01','INC-FLOOD-02','INC-ROAD-01','INC-WASTE-01','INC-WASTE-02']
for i in range(85):
 issue=issue_cycle[i%3]; id=add('Incident',f'INC-{i+1000:04d}',issue_type=issue,subtype={'WATERLOGGING':'STREET_STANDING_WATER','ROAD_DAMAGE':'POTHOLE','WASTE_ACCUMULATION':'BIN_OVERFLOW'}[issue],started_at=iso(i%90,hours=6),status='ENDED' if i%5==0 else 'ACTIVE',severity=['LOW','MODERATE','HIGH'][i%3]);incidents.append(id)
 loc=locations[(i+8)%len(locations)];edge('OCCURRED_AT',id,loc);edge('PART_OF',id,clusters[(i+3)%len(clusters)])
 target={'WATERLOGGING':all_drains[i%len(all_drains)],'ROAD_DAMAGE':roads[i%len(roads)],'WASTE_ACCUMULATION':waste[i%len(waste)]}[issue]
 edge('AFFECTS',id,target,association_status='REPORTED')

# multiple reports per incident; never each automatically becomes another occurrence
for i in range(254):
 target=incidents[i%len(incidents)];obj=add('Complaint',f'CMP-{i+1000:04d}',description=f'Synthetic report {i+1000} about repeated public issue linked to incident {target}',reported_at=iso(i%90,hours=9),source_channel='DEMO_PORTAL',source_kind='SYNTHETIC',status='ACCEPTED')
 edge('REPORTS',obj,target)

for i in range(55):
  type=['WATER_DEPTH_CM','ROAD_CONDITION','WASTE_VOLUME_L'][i%3]
  obs=add('Observation',f'OBS-{i+100:04d}',observation_type=type,observed_at=iso(i%90,hours=10),source_kind='SYNTHETIC',observation_basis='REPORTED',value_number=round((i%8+1)*3.5,1),unit={'WATER_DEPTH_CM':'cm','ROAD_CONDITION':'index','WASTE_VOLUME_L':'L'}[type])

for i in range(45):
 t=(all_drains+roads+waste+pipes)[(i*7)%(len(all_drains)+len(roads)+len(waste)+len(pipes))]
 snap=add('AssetConditionSnapshot',f'COND-{i+100:04d}',asset_id=t,observed_at=iso(i%90),condition=['REPORTED_GOOD','REPORTED_DEGRADED','UNKNOWN'][i%3],observation_method='SYNTHETIC_VISUAL_SURVEY')
 edge('CONDITION_OF',snap,t)

for name,role,dept in [('analyst','ANALYST','DEPT-COORD'),('drain-lead','DEPARTMENT_LEAD','DEPT-DRAIN'),('road-lead','DEPARTMENT_LEAD','DEPT-ROAD'),('waste-lead','DEPARTMENT_LEAD','DEPT-SAN'),('approver','APPROVER','DEPT-COORD')]:
 uid=add('OperatorAccount',f'OP-{name.upper()}',display_name=f'Synthetic {name}',role=role,department_id=dept,enabled=True)
 edge('HAS_OPERATOR',dept,uid)

obj={'schema_version':2,'fixture_id':'CIVICLY-SYNTHETIC-CITY-V2','description':'Deterministic synthetic 5-ward municipal network. No hidden causes/delayed inspection results are included. Results are illustrative, not real Varanasi infrastructure.','nodes':NODES,'relationships':EDGES,'ground_truth_visible_to_agent':False,'generator_version':'2.0','seed_city':'Fictional Civicly Demo City'}
out=ROOT/'contracts/seed_graph_expanded.json'
out.write_text(json.dumps(obj,indent=2)+'\n')
print('Seed created',len(NODES),'nodes',len(EDGES),'edges')
print('node labels:',dict(collections.Counter(n['label'] for n in NODES)))
