"""Separate synthetic situations on distinct assets; failed cases stay untouched."""
from pathlib import Path
from app.graph.schema import utc_now
from app.graph.models import digest
from app.services.evidence.writer import common
from app.services.complaints.service import ComplaintService
from app.services.evidence.service import EvidenceService
from app.services.operations.auth import Auth
from app.services.operations.storage import Storage
from app.services.responsibility.service import Responsibility
from app.services.http.service import request_identity
from cli.private import read_json,write_private
from .config import HostConfig,Case

def alternatives(config,repo,*,rehearsal=False):
 parent=Path(config.auth_store).parent;destination=parent/('host-rehearsal02.json' if rehearsal else 'host-clean.json')
 if destination.exists():raise ValueError('ALTERNATIVES_ALREADY_PREPARED')
 auth=Auth(config.auth_store);credentials=read_json(parent/'presenter-credentials.json',private=True)
 tokens={who:auth.login(who,credentials[who]) for who in ['OP-ANALYST','OP-ROAD-LEAD','OP-WATER-LEAD','OP-WASTE-LEAD']}
 try:
  at=utc_now();evidence='DEMO-REHEARSAL02-INVENTORY' if rehearsal else 'DEMO-ALTERNATIVE-INVENTORY'
  repo.create_node('Evidence',{**common(evidence,at),'recorded_at':at,'observed_at':at,'evidence_type':'SYNTHETIC_INVENTORY_SURVEY','summary':'Explicit independent synthetic road/pipe and waste-point inventory; no cause asserted','source_kind':'SYNTHETIC','source_record_id':'demo-independent-inventory','basis':'OBSERVED','reliability':'VERIFIED'})
  mapping={'ROAD-100':'ROAD-DEMO-HEALTHY','PIPE-100':'PIPE-DEMO-HEALTHY','WASTE-100':'WASTE-DEMO-DUMPING'}
  if rehearsal:mapping={'ROAD-100':'ROAD-DEMO-SUBGRADE-02','PIPE-100':'PIPE-DEMO-NORMAL-02','WASTE-100':'WASTE-DEMO-SERVICE-02'}
  locations={}
  for old,new in mapping.items():
   asset=repo.get_node(old);locrows=repo._read('MATCH (:InfrastructureAsset {id:$id})-[:LOCATED_AT]->(l:Location) RETURN l.id LIMIT 2',{'id':old});loc=repo.get_node(locrows[0][0]);newloc='LOC-'+new
   repo.create_node('Location',{**loc.properties,'id':newloc,'created_at':at,'updated_at':at,'name':'Independent synthetic location '+new})
   repo.create_node(asset.kind,{**asset.properties,'id':new,'created_at':at,'updated_at':at,'name':'Independent synthetic '+new})
   repo.create_relationship('LOCATED_AT',new,newloc,{'id':'LOCATED-'+new,'municipality_id':'demo-city','created_at':at,'source_evidence_id':evidence})
   dept,who=('DEPT-ROAD','OP-ROAD-LEAD') if old.startswith('ROAD') else ('DEPT-WATER','OP-WATER-LEAD') if old.startswith('PIPE') else ('DEPT-SAN','OP-WASTE-LEAD')
   own=Responsibility(repo,auth);sub=own.execute('submit',None,{'asset_id':new,'department_id':dept,'source_id':'DEMO-independent-inventory','source_record_id':new,'observed_at':at,'valid_from':at},request_id='DEMO-OWN-'+new,token=tokens[who]);own.execute('review',sub['id'],{'expected_hash':sub['expected_hash'],'reviewed':True,'reason':'Independent review of new synthetic responsibility'},request_id='DEMO-REVIEW-'+new,token=tokens['OP-ANALYST'])
   locations[new]=newloc
  batch='REHEARSAL02' if rehearsal else 'INDEPENDENT'
  repo.create_relationship('UNDERLIES',mapping['PIPE-100'],mapping['ROAD-100'],{'id':'DEMO-'+batch+'-UNDERLIES','municipality_id':'demo-city','created_at':at,'valid_from':at,'source_evidence_id':evidence,'association_status':'VERIFIED'})
  repo.create_relationship('COLLECTED_BY',mapping['WASTE-100'],'ROUTE-C03',{'id':'DEMO-'+batch+'-COLLECTED','municipality_id':'demo-city','created_at':at,'valid_from':at,'source_evidence_id':evidence})
  from app.services.demo.definitions import load,intake
  cases=[next(c for c in config.cases if c.issue=='WATERLOGGING')]
  for scenario,issue,asset in [('S03','ROAD_DAMAGE',mapping['ROAD-100']),('S05' if rehearsal else 'S06','WASTE_ACCUMULATION',mapping['WASTE-100'])]:
   command=intake(load()[scenario],issue);command.update(source_id='DEMO-'+batch+'-'+scenario,external_record_id=scenario,reported_at=at,occurred_at=at,location_id=locations[asset],asset_ids=[asset,mapping['PIPE-100']] if scenario=='S03' else [asset])
   received=ComplaintService(repo).intake(command)
   inv=EvidenceService(repo).execute({'operation':'open','request_id':request_identity(repo.graph.name,'OP-ANALYST',batch+'-'+scenario),'incident_ids':[received.incident_id],'cluster_id':received.cluster_id},auth.resolve(tokens['OP-ANALYST'])).entity_id
   cases.append(Case(scenario=scenario,issue=issue,investigation_id=inv,incident_id=received.incident_id,thread_id='DEMO-'+digest([repo.graph.name,inv])[:32]))
   if scenario in {'S05','S06'}:
    from app.events.service import Delivery
    with repo._session() as session:Delivery(repo,utc_now).store.write(session,[('service_policy_scope',inv,{'source_graph':repo.graph.name,'investigation_id':inv,'scenario':scenario})])
  new=HostConfig.model_validate({**config.model_dump(),'cases':[c.model_dump() for c in cases]})
  write_private(destination,new.model_dump(mode='json'))
  return {'host_config':str(destination),'cases':[c.model_dump() for c in cases],'retained_previous_cases':True,'distinct_assets':mapping}
 finally:
  for token in tokens.values():auth.logout(token)
