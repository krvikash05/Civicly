"""Explicit Gemini-only adapter over the accepted fenced worker; no paid fallback."""
from datetime import timedelta
from pathlib import Path
import httpx
from app.agents.provider import Gemini,ProviderSettings
from app.agents.policy import Permit
from app.agents.spending import Ledger,Pricing,DEFAULT_LEDGER
from app.agents.limits import CountBillingPolicy
from app.agents.checkpoints import RecoveryRequired,saver
from app.agents.models import InvestigationState
from app.events.runtime import Runtime
from app.graph.models import digest
from app.graph.schema import timestamp,utc_now
from app.memory.runtime import configured
from app.services.evidence.reader import Reader

class HostBlocked(RuntimeError):pass

def provider_settings(config):
 s=ProviderSettings(_env_file='.env').model_copy(update={'transient_retries':0,'retry_wait_budget':0})
 if s.model!=config.model or s.provider!='gemini' or s.key is None:raise HostBlocked('HOST_PROVIDER_CONFIGURATION_MISMATCH')
 Pricing(s.pricing_file).validate(s.model)
 if not CountBillingPolicy().nonbillable(s.model,Pricing(s.pricing_file).clock()):raise HostBlocked('COUNT_POLICY_REVIEW_REQUIRED')
 return s

def local_preflight(config,profile,repo,*,case_id=None):
 """No external model requests, allocations, source writes or quarantine clearance."""
 now=utc_now();mp=configured(profile.graph,config.memory_profile)
 if mp is None or mp.source_graphs!=[profile.graph]:raise HostBlocked('EXACT_DEMO_MEMORY_CAPABILITY_REQUIRED')
 settings=provider_settings(config)
 if not DEFAULT_LEDGER.is_file():raise HostBlocked('EXISTING_LEDGER_REQUIRED')
 ledger=Ledger(project_limit=settings.project_limit)
 with ledger.db() as db:
  if db.execute('SELECT count(*) FROM sessions').fetchone()[0] or db.execute("SELECT count(*) FROM request_holds WHERE status='OPEN'").fetchone()[0] or db.execute("SELECT count(*) FROM requests WHERE charged IS NULL").fetchone()[0]:raise HostBlocked('LEDGER_RECONCILIATION_REQUIRED')
  cfg=dict(db.execute('SELECT * FROM config').fetchone())
  if cfg['max_concurrent']!=1:raise HostBlocked('SEQUENTIAL_LEDGER_REQUIRED')
  if ledger.spent(db)>=cfg['project_cap']:raise HostBlocked('PROJECT_SPENDING_CAP')
  for c in config.cases:
   cap=db.execute('SELECT cap FROM cases WHERE id=?',(c.investigation_id,)).fetchone()
   if cap and cap[0]>cfg['case_cap']:raise HostBlocked('DEMO_CASE_CAP_INCREASE_DENIED')
 r=Reader(repo,now);checks=[]
 for c in config.cases:
  if case_id and c.investigation_id!=case_id:continue
  inv=r.node(c.investigation_id,'Investigation');incident=r.node(c.incident_id,'Incident')
  if inv.properties.get('thread_id') not in {None,c.thread_id} or incident.properties['issue_type']!=c.issue:raise HostBlocked('HOST_CASE_THREAD_BINDING')
  if c.incident_id not in {e.target for e in r.edges('INVESTIGATES',source=inv.id)}:raise HostBlocked('HOST_INCIDENT_BINDING')
  key='civicly:b10:'+profile.graph+':'+digest(c.thread_id)
  if repo.client.connection.exists(key,key+':quarantine'):raise HostBlocked('CASE_OWNERSHIP_OR_QUARANTINE_REQUIRES_OPERATOR')
  saved=saver(profile).get_tuple({'configurable':{'thread_id':c.thread_id}})
  if saved:
   state=InvestigationState.model_validate(saved.checkpoint['channel_values']['data'])
   if (state.graph,state.investigation_id,state.thread_id)!=(profile.graph,c.investigation_id,c.thread_id) or state.budget!=config.budget:raise HostBlocked('CHECKPOINT_SCOPE_OR_BUDGET_MISMATCH')
   if 'WRITE_OUTCOME_UNKNOWN' in state.errors:
    from .reconciliation import valid_reconciliation
    if not valid_reconciliation(config,profile,repo,c,state):raise HostBlocked('CASE_REQUIRES_OPERATOR_NO_RETRY')
   if state.pause_reason and ('RECOVERY' in state.pause_reason or state.pause_reason in {'DEPENDENCY_UNAVAILABLE','BUDGET_EXHAUSTED','TOKEN_BUDGET','TOOL_BUDGET'}):raise HostBlocked('CASE_REQUIRES_OPERATOR_NO_RETRY')
  elif inv.properties.get('thread_id'):raise HostBlocked('BOUND_CHECKPOINT_MISSING')
  checks.append({'investigation_id':c.investigation_id,'thread_id':c.thread_id,'issue':c.issue,'checkpoint_present':bool(saved),'quarantine':False})
 if case_id and not checks:raise HostBlocked('CASE_NOT_HOST_AUTHORIZED')
 return {'checked_at':now,'source_graph':profile.graph,'config_sha256':config.fingerprint,'configured_model':config.model,'cases':checks,'ledger_caps_nusd':cfg,'no_external_provider_requests':True}

async def model_preflight(config):
 """Authorized metadata-only compatibility check; no count/generation call or retry."""
 s=provider_settings(config)
 async with httpx.AsyncClient(timeout=s.timeout,follow_redirects=False) as client:
  try:response=await client.get('https://generativelanguage.googleapis.com/v1beta/models/'+s.model,headers={'x-goog-api-key':s.key.get_secret_value()})
  except httpx.HTTPError:raise HostBlocked('MODEL_METADATA_TRANSPORT_UNAVAILABLE') from None
 if response.status_code!=200:raise HostBlocked('MODEL_METADATA_HTTP_'+str(response.status_code))
 try:
  value=response.json()
  if value.get('name')!='models/'+s.model or not {'generateContent','countTokens'}<=set(value.get('supportedGenerationMethods',[])):raise ValueError()
  if value['inputTokenLimit']<s.max_input_tokens or value['outputTokenLimit']<s.max_output_tokens:raise ValueError()
 except (ValueError,KeyError,TypeError):raise HostBlocked('MODEL_METADATA_INCOMPATIBLE') from None
 return {'checked_at':utc_now(),'config_sha256':config.fingerprint,'configured_model':s.model,'metadata_name':value['name'],'metadata_version':str(value.get('version','UNAVAILABLE'))[:100],'input_token_limit':value['inputTokenLimit'],'output_token_limit':value['outputTokenLimit'],'count_generation_attempts':0,'status':'COMPATIBLE'}

class LiveRuntime(Runtime):
 def __init__(self,config,profile,repo,clock,*,planning_service,compatibility):
  self.config,self.compatibility=config,compatibility
  super().__init__(profile,config.profile,repo,clock,memory_path=config.memory_profile,planning_service=planning_service,budget=config.budget)
 def thread(self,inv):
  case=next((c for c in self.config.cases if c.investigation_id==inv),None)
  if case is None:raise RecoveryRequired('CASE_NOT_HOST_AUTHORIZED')
  return case.thread_id
 async def handle(self,claim):
  from .source import source_writer
  with source_writer(self.repo):
   return await super().handle(claim)
 def model_for(self,inv,thread):
  if self.thread(inv)!=thread:raise RecoveryRequired('HOST_THREAD_MISMATCH')
  proof=self.compatibility
  if proof.get('status')!='COMPATIBLE' or proof.get('config_sha256')!=self.config.fingerprint or not timestamp(utc_now())-timedelta(hours=1)<=timestamp(proof['checked_at'])<=timestamp(utc_now()):raise HostBlocked('RECENT_MODEL_COMPATIBILITY_REQUIRED')
  local_preflight(self.config,self.profile,self.repo,case_id=inv)
  permit=Permit.explicit_live(approved=True,investigation_id=inv,thread_id=thread,milestone='FRONTEND-BACKEND-DEMO')
  return Gemini(provider_settings(self.config),permit=permit)
