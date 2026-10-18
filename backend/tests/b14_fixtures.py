"""Authored simulated observations through real authenticated B09/B13 services."""
from app.active import active_scope
from app.services.operations.service import Operations
from app.services.operations.migration import OperationsMigration
from app.services.operations.verification import REQUIRED
from tests.b12_fixtures import prepared
from tests.b13_fixtures import auth_setup
from tests.integration.test_operations_runtime import approved

def prepare(db,tmp_path,memory,issue):
 p,r,clock,path,inv,draft,planning=prepared(db,tmp_path,memory,issue,remedial=True)
 auth,tokens=auth_setup(tmp_path/'auth.sqlite3');OperationsMigration(db,p.graph).apply()
 ops=Operations(planning,auth,clock=clock)
 return p,r,clock,path,inv,draft,planning,auth,tokens,ops

class Run:
 def __init__(self,r,clock,ops,tokens,issue):
  self.r,self.clock,self.ops,self.tokens,self.issue=r,clock,ops,tokens,issue;self.n=0;self.assignment_index=0
  self.lead={'WATERLOGGING':'OP-DRAIN-LEAD','ROAD_DAMAGE':'OP-ROAD-LEAD','WASTE_ACCUMULATION':'OP-WASTE-LEAD'}[issue]
 def key(self):self.n+=1;return 'B14-command-'+str(self.n)
 async def call(self,command,operator=None,**kw):
  return await self.ops.execute(command,token=self.tokens[operator or self.lead],**kw)
 async def begin(self,planning,draft):
  b,saved,pending,decision=await approved(self.ops,planning,draft,self.tokens,'B14')
  self.b,self.saved=b,saved
  self.w=await self.call({**b,'operation':'order','request_id':self.key(),'approval_id':decision['id'],'task_id':b['assignments'][0]['task_id']},'OP-APPROVER')
  await self.call({'operation':'update','request_id':self.key(),'work_order_id':self.w['id'],'expected_hash':self.hash(),'new_status':'ASSIGNED','reason':'Assigned simulated departmental actor'})
  await self.progress('START')
  return self.w
 def hash(self):return self.r.get_node(self.w['id'],'WorkOrder').content_hash
 async def progress(self,action,evidence_ids=None,**kw):
  q={'operation':'progress','request_id':self.key(),'work_order_id':self.w['id'],'expected_hash':self.hash(),'action':action,'reason':'Authored simulated '+action,'evidence_ids':evidence_ids or []}
  return q,await self.call(q,**kw)
 async def report(self,purpose,observations):
  a=self.b['assignments'][self.assignment_index];key=self.key()
  async def command(c,review=False):
   key=self.key();c['request_id']=key
   q={'operation':'inspect','request_id':key,'work_order_id':self.w['id'],'expected_hash':self.hash(),'purpose':purpose,'command':c}
   if review:q['review_reason']='Independent authenticated review of authored synthetic measurements'
   out=await self.call(q,reviewer_token=self.tokens['OP-ANALYST'] if review else None)
   return q,out
  _,created=await command({'operation':'request_inspection','investigation_id':self.saved['draft']['investigation_id'],'asset_ids':a['target_ids'],'department_id':a['department_id'],'inspection_type':'B14_FOLLOWUP' if purpose=='FOLLOWUP' else a['action_type']})
  id=created['entity_id']
  for status in ['REQUESTED','SCHEDULED','IN_PROGRESS']:
   self.clock.advance();c={'operation':'transition_inspection','inspection_id':id,'expected_hash':self.r.get_node(id).content_hash,'status':status}
   if status=='SCHEDULED':c['scheduled_at']=self.clock()
   await command(c)
  self.clock.advance()
  obs=observations(self.clock())
  q,out=await command({'operation':'report_inspection','inspection_id':id,'expected_hash':self.r.get_node(id).content_hash,'source_id':'B14-field-'+key,'record_id':key,'source_kind':'SYNTHETIC','observations':obs},True)
  return q,out
 def observation(self,code,at,value=None,unit=None):
  return {'asset_id':self.b['assignments'][self.assignment_index]['target_ids'][0],'code':code,'statement':'Authored synthetic '+code,'method':'DIRECT_SYNTHETIC_FIELD_TEST','observed_at':at,'result':'OBSERVED','value':value,'unit':unit}
 async def complete(self,fail=False):
  q,report=await self.report('COMPLETION',lambda at:[self.observation('ACTION_FAILED' if fail else 'ACTION_COMPLETED',at)])
  pq,result=await self.progress('FAIL' if fail else 'COMPLETE',[report['entity_id']]);return q,report,pq,result
 async def followup(self,adverse=0.0):
  self.clock.advance();start=self.clock()
  # Request/start inspection before authoring later controlled-time observations.
  def observations(at):
   if self.issue=='WASTE_ACCUMULATION':
    from datetime import timedelta
    pickup=at;self.clock.advance(25*3600);end=self.clock()
    return [self.observation('SCHEDULED_PICKUPS',pickup,1.0,'pickups'),self.observation('ACTUAL_PICKUPS',pickup,1.0,'pickups'),self.observation('REACCUMULATION_WINDOW',end,24.0,'hours'),self.observation('WASTE_REACCUMULATION',end,adverse,'boolean')]
   first=at;self.clock.advance();return [self.observation(REQUIRED[self.issue][0],first),self.observation(REQUIRED[self.issue][1],self.clock(),adverse,'boolean')]
  q,rep=await self.report('FOLLOWUP',observations);self.clock.advance()
  return {'operation':'evaluate','request_id':self.key(),'work_order_id':self.w['id'],'expected_hash':self.hash(),'evidence_ids':[rep['entity_id']],'window_start':start,'window_end':self.clock()},rep
