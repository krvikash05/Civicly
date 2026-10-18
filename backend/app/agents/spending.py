"""Private auxiliary accounting, not municipal knowledge or a Google billing hard cap."""
from contextlib import contextmanager
from datetime import datetime,timezone
from decimal import Decimal,ROUND_CEILING
import json,os,sqlite3,time
from pathlib import Path
from uuid import uuid4
from app.active import ROOT

NANO=1_000_000_000
DEFAULT_LEDGER=ROOT/'.runtime/ai-spend.sqlite3'
class SpendError(RuntimeError):pass

def dollars(value):
    d=Decimal(str(value))
    if not d.is_finite() or d<=0:raise ValueError('Positive finite spending limit required')
    return int((d*NANO).to_integral_value(rounding=ROUND_CEILING))

class Pricing:
    def __init__(self,path=None,*,clock=lambda:datetime.now(timezone.utc)):
        path=path or Path(__file__).parent/'pricing/gemini-3.8-flash-standard-2026-10.json'
        self.data=json.loads(Path(path).read_text());self.clock=clock
        self.version=self.data['version']
        # Exact integer nanodollars/token; no float currency arithmetic.
        self.rates={k:int(Decimal(v)*1000) for k,v in self.data['usd_per_million'].items()}
        if any(Decimal(v)*1000!=self.rates[k] for k,v in self.data['usd_per_million'].items()):raise ValueError('Unsupported rate precision')
    def validate(self,model):
        at=self.clock()
        if model!=self.data['model'] or self.data['tier']!='standard' or self.data['modality']!='text':raise SpendError('PRICING_MODEL_UNSUPPORTED')
        if not datetime.fromisoformat(self.data['valid_from'].replace('Z','+00:00'))<=at<datetime.fromisoformat(self.data['valid_until'].replace('Z','+00:00')):raise SpendError('PRICING_EXPIRED')
    def estimate(self,input_bytes,max_output,*,input_tokens=None):
        # Financial fence only; a known token count may require a larger reservation.
        return max(input_bytes+1024,input_tokens or 0)*self.rates['input']+2*max_output*max(self.rates['output'],self.rates['thinking'])
    def actual(self,usage):
        usage=dict(usage);usage.setdefault('thoughtsTokenCount',0)
        keys=['promptTokenCount','candidatesTokenCount','thoughtsTokenCount','totalTokenCount']
        if any(type(usage.get(k))is not int or usage[k]<0 for k in keys):return None
        cached=usage.get('cachedContentTokenCount',0)
        if type(cached)is not int or not 0<=cached<=usage['promptTokenCount']:return None
        if sum(usage[k] for k in keys[:3])!=usage['totalTokenCount']:return None
        return (usage['promptTokenCount']-cached)*self.rates['input']+cached*self.rates['cached_input']+usage['candidatesTokenCount']*self.rates['output']+usage['thoughtsTokenCount']*self.rates['thinking']

class Ledger:
    def __init__(self,path=DEFAULT_LEDGER,*,project_limit=None,default_case_limit=None,max_concurrent=None,complex_case_limit=None):
        self.path=Path(path);self.path.parent.mkdir(parents=True,mode=0o700,exist_ok=True)
        if self.path.is_symlink():raise SpendError('UNSAFE_LEDGER_FILE')
        fd=os.open(self.path,os.O_CREAT|os.O_RDWR,0o600);os.close(fd)
        if self.path.stat().st_mode&0o077:raise SpendError('PRIVATE_LEDGER_REQUIRED')
        with self.db() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS config(id INTEGER PRIMARY KEY,project_cap INTEGER,case_cap INTEGER,max_concurrent INTEGER);
            CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY,cap INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions(owner TEXT PRIMARY KEY,case_id TEXT,thread TEXT,heartbeat REAL);
            CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY,case_id TEXT,thread TEXT,model TEXT,milestone TEXT,pricing TEXT,reserved INTEGER,charged INTEGER,status TEXT,usage TEXT,error TEXT,created REAL);
            CREATE TABLE IF NOT EXISTS holds(id INTEGER PRIMARY KEY,reason TEXT);
            CREATE TABLE IF NOT EXISTS config_changes(id INTEGER PRIMARY KEY,previous TEXT,current TEXT,reason TEXT,created REAL);
            CREATE TABLE IF NOT EXISTS warnings(scope TEXT,threshold INTEGER,created REAL,PRIMARY KEY(scope,threshold));''')
            columns={r[1] for r in db.execute('PRAGMA table_info(config)')}
            if 'complex_cap' not in columns:db.execute('ALTER TABLE config ADD COLUMN complex_cap INTEGER NOT NULL DEFAULT 1500000000')
            db.execute('INSERT OR IGNORE INTO config VALUES(1,?,?,?,?)',(dollars(project_limit if project_limit is not None else 8),dollars(default_case_limit if default_case_limit is not None else '.50'),max_concurrent if max_concurrent is not None else 1,dollars(complex_case_limit if complex_case_limit is not None else '1.50')))
            row=db.execute('SELECT * FROM config WHERE id=1').fetchone()
            if any(value is not None and row[column]!=expected for column,value,expected in [('project_cap',project_limit,dollars(project_limit) if project_limit is not None else None),('case_cap',default_case_limit,dollars(default_case_limit) if default_case_limit is not None else None),('max_concurrent',max_concurrent,max_concurrent),('complex_cap',complex_case_limit,dollars(complex_case_limit) if complex_case_limit is not None else None)]):raise SpendError('PERSISTED_PROJECT_LIMIT_MISMATCH; explicit operator migration required')
            db.executescript("""CREATE TABLE IF NOT EXISTS request_holds(request_id TEXT PRIMARY KEY,reason TEXT,status TEXT NOT NULL DEFAULT 'OPEN',created REAL);
            CREATE TABLE IF NOT EXISTS legacy_hold_links(id INTEGER PRIMARY KEY,mapped_at REAL);
            CREATE TABLE IF NOT EXISTS accounting_events(id INTEGER PRIMARY KEY,request_id TEXT,operation TEXT,operator TEXT,reason TEXT,payload TEXT,created REAL);
            CREATE TRIGGER IF NOT EXISTS immutable_accounting_update BEFORE UPDATE ON accounting_events BEGIN SELECT RAISE(ABORT,'IMMUTABLE_ACCOUNTING_AUDIT'); END;
            CREATE TRIGGER IF NOT EXISTS immutable_accounting_delete BEFORE DELETE ON accounting_events BEGIN SELECT RAISE(ABORT,'IMMUTABLE_ACCOUNTING_AUDIT'); END;
            CREATE TRIGGER IF NOT EXISTS immutable_config_update BEFORE UPDATE ON config_changes BEGIN SELECT RAISE(ABORT,'IMMUTABLE_ACCOUNTING_AUDIT'); END;
            CREATE TRIGGER IF NOT EXISTS immutable_config_delete BEFORE DELETE ON config_changes BEGIN SELECT RAISE(ABORT,'IMMUTABLE_ACCOUNTING_AUDIT'); END;
            CREATE TABLE IF NOT EXISTS token_usage(request_id TEXT PRIMARY KEY,thread TEXT,reserved INTEGER,consumed INTEGER);
            CREATE TABLE IF NOT EXISTS token_floors(thread TEXT PRIMARY KEY,baseline INTEGER);""")
            # Legacy global hold retained as history; link every offending request once.
            for old_hold in db.execute('SELECT * FROM holds').fetchall():
                if db.execute('SELECT 1 FROM legacy_hold_links WHERE id=?',(old_hold['id'],)).fetchone():continue
                offenders=db.execute("SELECT id FROM requests WHERE status='SETTLED_OVER_RESERVATION'").fetchall()
                for request in offenders or [{'id':'LEGACY-UNATTRIBUTED-'+str(old_hold['id'])}]:
                    db.execute('INSERT OR IGNORE INTO request_holds VALUES(?,?,?,?)',(request['id'],old_hold['reason'],'OPEN',time.time()))
                db.execute('INSERT OR IGNORE INTO legacy_hold_links VALUES(?,?)',(old_hold['id'],time.time()))
    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path,timeout=5,isolation_level=None);db.row_factory=sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA busy_timeout=5000')
        try:yield db
        finally:db.close()
    @contextmanager
    def transaction(self):
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            try:yield db;db.execute('COMMIT')
            except BaseException:db.execute('ROLLBACK');raise
    def configure_case(self,case_id,limit=None):
        with self.transaction() as db:
            default=db.execute('SELECT case_cap,project_cap,complex_cap FROM config').fetchone();old=db.execute('SELECT cap FROM cases WHERE id=?',(case_id,)).fetchone()
            if old and limit is None:return
            cap=dollars(limit) if limit is not None else default[0]
            if cap>min(default[1],default[2]):raise SpendError('CASE_CAP_EXCEEDS_PROJECT')
            old=db.execute('SELECT cap FROM cases WHERE id=?',(case_id,)).fetchone()
            if old and old[0]!=cap:
                # A particular explicitly opted-in invocation may raise, never erase usage.
                if limit is None or cap<old[0]:raise SpendError('CASE_LIMIT_CHANGE_REQUIRES_EXPLICIT_INCREASE')
                db.execute('UPDATE cases SET cap=? WHERE id=?',(cap,case_id))
            else:db.execute('INSERT OR IGNORE INTO cases VALUES(?,?)',(case_id,cap))
            self.event(db,case_id,'CASE_ALLOCATION','TRUSTED_HOST','Explicit allocation or new-case default',{'previous':old[0] if old else None,'current':cap})
    def acquire(self,case_id,thread,owner):
        with self.transaction() as db:
            maximum=db.execute('SELECT max_concurrent FROM config').fetchone()[0]
            if db.execute('SELECT count(*) FROM sessions').fetchone()[0]>=maximum:raise SpendError('LIVE_CONCURRENCY_LIMIT')
            db.execute('INSERT INTO sessions VALUES(?,?,?,?)',(owner,case_id,thread,time.time()))
    def heartbeat(self,owner):
        with self.transaction() as db:
            if db.execute('UPDATE sessions SET heartbeat=? WHERE owner=?',(time.time(),owner)).rowcount!=1:raise SpendError('LIVE_SESSION_LOST')
    def release(self,owner):
        # No expiry-based auto takeover: stop previous process and reconcile first.
        with self.transaction() as db:db.execute('DELETE FROM sessions WHERE owner=?',(owner,))
    @staticmethod
    def spent(db,case=None):
        sql='SELECT coalesce(sum(CASE WHEN charged IS NULL THEN reserved ELSE charged END),0) FROM requests'
        return db.execute(sql+(' WHERE case_id=?' if case else ''),(case,) if case else ()).fetchone()[0]
    def reserve(self,id,case,thread,model,milestone,pricing,amount,owner,*,token_reservation=None,token_limit=None,base_tokens=0):
        if type(amount)is not int or amount<=0:raise SpendError('INVALID_RESERVATION')
        with self.transaction() as db:
            if db.execute("SELECT count(*) FROM request_holds WHERE status='OPEN'").fetchone()[0]:raise SpendError('LEDGER_RECONCILIATION_REQUIRED')
            session=db.execute('SELECT * FROM sessions WHERE owner=?',(owner,)).fetchone()
            if not session or (session['case_id'],session['thread'])!=(case,thread):raise SpendError('LIVE_SESSION_REQUIRED')
            if db.execute('SELECT id FROM requests WHERE id=?',(id,)).fetchone():raise SpendError('REQUEST_ALREADY_RESERVED; reconcile, never blindly rebill')
            cap=db.execute('SELECT cap FROM cases WHERE id=?',(case,)).fetchone()
            if not cap:raise SpendError('CASE_ALLOCATION_REQUIRED')
            for scope,total,limit in [('project',self.spent(db),db.execute('SELECT project_cap FROM config').fetchone()[0]),('case:'+case,self.spent(db,case),cap[0])]:
                if total+amount>limit:raise SpendError('PROJECT_SPENDING_CAP' if scope=='project' else 'INVESTIGATION_SPENDING_CAP')
                for threshold in [50,80,95,100]:
                    if (total+amount)*100>=limit*threshold:db.execute('INSERT OR IGNORE INTO warnings VALUES(?,?,?)',(scope,threshold,time.time()))
            if token_reservation is not None:
                if type(token_reservation)is not int or token_reservation<0 or type(token_limit)is not int or type(base_tokens)is not int or base_tokens<0:raise SpendError('INVALID_TOKEN_ACCOUNTING')
                current=self.token_total(db,thread);floor=max(0,base_tokens-current)
                if max(base_tokens,current)+token_reservation>token_limit:raise SpendError('TOKEN_BUDGET')
                db.execute('INSERT OR IGNORE INTO token_floors VALUES(?,0)',(thread,))
                db.execute('UPDATE token_floors SET baseline=baseline+? WHERE thread=?',(floor,thread))
                db.execute('INSERT INTO token_usage VALUES(?,?,?,NULL)',(id,thread,token_reservation))
            self.event(db,id,'RESERVE','PROVIDER','Atomic request reservation',{'nanodollars':amount,'token_allowance':token_reservation})
            db.execute('INSERT INTO requests VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(id,case,thread,model,milestone,pricing,amount,None,'RESERVED',None,None,time.time()))
    def reconcile(self,id,actual,usage,category=None):
        if actual is not None and (type(actual)is not int or actual<0):raise SpendError('INVALID_RECONCILIATION_AMOUNT')
        with self.transaction() as db:
            old=db.execute('SELECT * FROM requests WHERE id=?',(id,)).fetchone()
            if not old:raise SpendError('RESERVATION_MISSING')
            encoded=json.dumps(usage,sort_keys=True)
            if old['status'].startswith('SETTLED'):
                if old['charged']!=actual or old['usage']!=encoded:raise SpendError('RECONCILIATION_CONFLICT')
                return
            status='SETTLED' if actual is not None else 'UNCERTAIN'
            if actual is not None and actual>old['reserved']:
                status='SETTLED_OVER_RESERVATION';db.execute('INSERT OR IGNORE INTO request_holds VALUES(?,?,?,?)',(id,'Actual cost exceeds reservation; verify pricing/usage and caps','OPEN',time.time()))
            from .tokens import total_usage
            db.execute('UPDATE token_usage SET consumed=? WHERE request_id=?',(total_usage(usage),id))
            self.event(db,id,'RECONCILE','PROVIDER',category or status,{'charged':actual,'usage':usage,'status':status})
            db.execute('UPDATE requests SET charged=?,status=?,usage=?,error=? WHERE id=?',(actual,status,encoded,category,id))
    def reconcile_count(self,id,*,counted_input_tokens,outcome,policy_id,nonbillable):
        # This is a host-only accounting interface, not an agent tool or hold-clear API.
        if not id.startswith('AI-COUNT-') or type(nonbillable)is not bool or not policy_id or not outcome:raise SpendError('COUNT_ACCOUNTING_BINDING_REQUIRED')
        if counted_input_tokens is not None and (type(counted_input_tokens)is not int or counted_input_tokens<0):raise SpendError('INVALID_PROVIDER_COUNT')
        usage={'operation':'COUNT_TOKENS','provider_count_tokens':counted_input_tokens,'outcome':outcome,
            'billing_policy':policy_id,'count_is_not_generation_usage':True}
        self.reconcile(id,0 if nonbillable else None,usage,'COUNT_NONBILLABLE_'+outcome if nonbillable else 'COUNT_BILLING_UNCONFIRMED')
        return 'NONBILLABLE_SETTLED_ZERO' if nonbillable else 'UNCERTAIN_RESERVATION_HELD'
    def summary(self,case=None):
        with self.db() as db:
            cap=db.execute('SELECT project_cap FROM config').fetchone()[0];total=self.spent(db)
            case_row=db.execute('SELECT cap FROM cases WHERE id=?',(case,)).fetchone() if case else None
            return {'currency':'USD','unit':'nanodollars','configuration':dict(db.execute('SELECT * FROM config').fetchone()),'project_cap':cap,'project_accounted':total,'project_remaining':max(0,cap-total),
                'case_cap':case_row[0] if case_row else None,'case_accounted':self.spent(db,case) if case else None,
                'uncertain_requests':db.execute("SELECT count(*) FROM requests WHERE status IN ('RESERVED','UNCERTAIN')").fetchone()[0],
                'holds':[dict(row) for row in db.execute("SELECT * FROM request_holds WHERE status='OPEN'")],'sessions':[dict(row) for row in db.execute('SELECT * FROM sessions')],
                'warnings':[dict(row) for row in db.execute('SELECT * FROM warnings ORDER BY scope,threshold')],
                'accounting_scope':'Managed requests since B10-O; historical/external billing unknown; not a Google hard cap'}

    def update_limits(self,*,reason,project_limit=None,default_case_limit=None,max_concurrent=None,complex_case_limit=None):
        if not isinstance(reason,str) or not reason.strip():raise SpendError('OPERATOR_REASON_REQUIRED')
        with self.transaction() as db:
            if db.execute('SELECT count(*) FROM sessions').fetchone()[0]:raise SpendError('STOP_LIVE_SESSIONS_BEFORE_CONFIG_CHANGE')
            old=dict(db.execute('SELECT * FROM config WHERE id=1').fetchone());new=dict(old)
            if project_limit is not None:new['project_cap']=dollars(project_limit)
            if default_case_limit is not None:new['case_cap']=dollars(default_case_limit)
            if complex_case_limit is not None:new['complex_cap']=dollars(complex_case_limit)
            if max_concurrent is not None:
                if type(max_concurrent)is not int or not 1<=max_concurrent<=4:raise SpendError('INVALID_CONCURRENCY_LIMIT')
                new['max_concurrent']=max_concurrent
            if new['project_cap']<self.spent(db) or new['case_cap']>new['project_cap']:raise SpendError('LIMIT_BELOW_ACCOUNTED_USAGE')
            db.execute('UPDATE config SET project_cap=?,case_cap=?,max_concurrent=?,complex_cap=? WHERE id=1',(new['project_cap'],new['case_cap'],new['max_concurrent'],new['complex_cap']))
            db.execute('INSERT INTO config_changes(previous,current,reason,created) VALUES(?,?,?,?)',(json.dumps(old),json.dumps(new),reason,time.time()))

    @staticmethod
    def event(db,id,operation,operator,reason,payload):
        db.execute('INSERT INTO accounting_events(request_id,operation,operator,reason,payload,created) VALUES(?,?,?,?,?,?)',(id,operation,operator,reason,json.dumps(payload,sort_keys=True),time.time()))
    @staticmethod
    def token_total(db,thread):
        floor=db.execute('SELECT baseline FROM token_floors WHERE thread=?',(thread,)).fetchone()
        return (floor[0] if floor else 0)+db.execute('SELECT coalesce(sum(coalesce(consumed,reserved)),0) FROM token_usage WHERE thread=?',(thread,)).fetchone()[0]
    def thread_tokens(self,thread):
        with self.db() as db:return self.token_total(db,thread)
    def inspect_hold(self,id):
        with self.db() as db:
            hold=db.execute('SELECT * FROM request_holds WHERE request_id=?',(id,)).fetchone()
            request=db.execute('SELECT * FROM requests WHERE id=?',(id,)).fetchone()
            return {'hold':dict(hold) if hold else None,'request':dict(request) if request else None,'caps':dict(db.execute('SELECT * FROM config').fetchone()),'project_accounted':self.spent(db),'case_accounted':self.spent(db,request['case_id']) if request else None}
    def resolve_hold(self,id,*,authorized,operator,reason,verified_pricing,usage_sha256,evidence_ref,pricing=None):
        import hashlib
        if authorized is not True or not all(isinstance(v,str) and v.strip() for v in [operator,reason,evidence_ref]):raise SpendError('EXPLICIT_OPERATOR_AUTHORIZATION_REQUIRED')
        with self.transaction() as db:
            if db.execute('SELECT count(*) FROM sessions').fetchone()[0]:raise SpendError('STOP_LIVE_SESSIONS_BEFORE_RECONCILIATION')
            hold=db.execute("SELECT * FROM request_holds WHERE request_id=? AND status='OPEN'",(id,)).fetchone()
            request=db.execute('SELECT * FROM requests WHERE id=?',(id,)).fetchone()
            if not hold or not request:raise SpendError('EXACT_OPEN_HOLD_AND_REQUEST_REQUIRED')
            if request['status']!='SETTLED_OVER_RESERVATION' or request['charged'] is None or not request['usage']:raise SpendError('BILLING_UNRESOLVED')
            if request['pricing']!=verified_pricing or hashlib.sha256(request['usage'].encode()).hexdigest()!=usage_sha256:raise SpendError('VERIFIED_ACCOUNTING_BINDING_REQUIRED')
            tariff=pricing or Pricing()
            if tariff.version!=verified_pricing or tariff.data['model']!=request['model'] or tariff.actual(json.loads(request['usage']))!=request['charged']:raise SpendError('SETTLED_USAGE_REPRICING_REQUIRED')
            config=db.execute('SELECT * FROM config').fetchone();case=db.execute('SELECT cap FROM cases WHERE id=?',(request['case_id'],)).fetchone()
            if self.spent(db)>config['project_cap'] or self.spent(db,request['case_id'])>case[0]:raise SpendError('CAP_RECONCILIATION_REQUIRED')
            self.event(db,id,'RESOLVE_HOLD',operator,reason,{'request':dict(request),'evidence_ref':evidence_ref,'verified_pricing':verified_pricing,'usage_sha256':usage_sha256,'caps':dict(config)})
            db.execute("UPDATE request_holds SET status='RESOLVED' WHERE request_id=?",(id,))

if __name__=='__main__':
    from .spending_cli import main
    main()
