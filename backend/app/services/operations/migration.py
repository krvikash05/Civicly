"""Additive operational companion indexes, reusing supported migration readiness."""
import json,hashlib
from pathlib import Path
from app.graph.migration import MigrationRunner,MigrationError
from app.graph.schema import utc_now
from app.services.planning.storage import PlanMigration
PLAN=Path(__file__).resolve().parents[2]/'graph/migrations/0005_operations.json'
class OperationsMigration:
 def __init__(self,client,name):
  self.base=MigrationRunner(client,name);self.graph=self.base.graph;self.client=client
  self.plan=json.loads(PLAN.read_text());self.checksum=hashlib.sha256(PLAN.read_bytes()).hexdigest()
  if self.base.checksum!=self.plan['requires_0001_sha256']:raise MigrationError('0001 mismatch')
 def status(self):
  rows=self.graph.ro_query('MATCH (m:CivicOperationsMigration {id:$id}) RETURN m.checksum,m.state LIMIT 2',params={'id':'0005'}).result_set
  if len(rows)>1 or rows and (rows[0][0]!=self.checksum or rows[0][1] not in {'APPLYING','FAILED','READY'}):raise MigrationError('0005 checksum mismatch')
  ready=bool(rows and rows[0][1]=='READY')
  if ready:
   for key in ['indexes','constraints']:
    for spec in self.plan[key]:self.base._wait(key,spec,.1)
  return {'id':'0005','ready':ready,'checksum':self.checksum}
 def apply(self,retry_failed=False):
  if not PlanMigration(self.client,self.graph.name).status()['ready']:raise MigrationError('0004 not READY')
  if not self.base.status()['ready']:raise MigrationError('0001 not READY')
  lock=self.client.connection.lock('civicly:operations-migration:'+self.graph.name,timeout=30,blocking_timeout=1)
  if not lock.acquire():raise MigrationError('Migration busy')
  def state(value):self.graph.query('MERGE (m:CivicOperationsMigration {id:$id}) SET m.checksum=$sha,m.state=$state,m.updated_at=$at',params={'id':'0005','sha':self.checksum,'state':value,'at':utc_now()})
  try:
   if self.status()['ready']:return self.status()
   state('APPLYING')
   for spec in self.plan['indexes']:self.base._ensure_index(spec)
   for spec in self.plan['constraints']:self.base._ensure_constraint(spec,retry_failed)
   state('READY');return self.status()
  except Exception:state('FAILED');raise
  finally:lock.release()
