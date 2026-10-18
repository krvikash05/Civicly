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
    def estimate(self,input_bytes,max_output):
        # UTF8 bytes + fixed framing allowance, double output ceiling for safety.
        return (input_bytes+1024)*self.rates['input']+2*max_output*max(self.rates['output'],self.rates['thinking'])
    def actual(self,usage):
        usage=dict(usage);usage.setdefault('thoughtsTokenCount',0)
        keys=['promptTokenCount','candidatesTokenCount','thoughtsTokenCount','totalTokenCount']
        if any(type(usage.get(k))is not int or usage[k]<0 for k in keys):return None
        cached=usage.get('cachedContentTokenCount',0)
        if type(cached)is not int or not 0<=cached<=usage['promptTokenCount']:return None
        if sum(usage[k] for k in keys[:3])!=usage['totalTokenCount']:return None
        return (usage['promptTokenCount']-cached)*self.rates['input']+cached*self.rates['cached_input']+usage['candidatesTokenCount']*self.rates['output']+usage['thoughtsTokenCount']*self.rates['thinking']

class Ledger:
    def __init__(self,path=DEFAULT_LEDGER,*,project_limit=None,default_case_limit=None,max_concurrent=None):
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
            db.execute('INSERT OR IGNORE INTO config VALUES(1,?,?,?)',(dollars(project_limit if project_limit is not None else 6),dollars(default_case_limit if default_case_limit is not None else '.15'),max_concurrent if max_concurrent is not None else 1))
            row=db.execute('SELECT * FROM config WHERE id=1').fetchone()
            if any(value is not None and row[column]!=expected for column,value,expected in [('project_cap',project_limit,dollars(project_limit) if project_limit is not None else None),('case_cap',default_case_limit,dollars(default_case_limit) if default_case_limit is not None else None),('max_concurrent',max_concurrent,max_concurrent)]):raise SpendError('PERSISTED_PROJECT_LIMIT_MISMATCH; explicit operator migration required')
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
            default=db.execute('SELECT case_cap,project_cap FROM config').fetchone();cap=dollars(limit) if limit is not None else default[0]
            if cap>default[1]:raise SpendError('CASE_CAP_EXCEEDS_PROJECT')
            old=db.execute('SELECT cap FROM cases WHERE id=?',(case_id,)).fetchone()
            if old and old[0]!=cap:
                # A particular explicitly opted-in invocation may raise, never erase usage.
                if limit is None or cap<old[0]:raise SpendError('CASE_LIMIT_CHANGE_REQUIRES_EXPLICIT_INCREASE')
                db.execute('UPDATE cases SET cap=? WHERE id=?',(cap,case_id))
            else:db.execute('INSERT OR IGNORE INTO cases VALUES(?,?)',(case_id,cap))
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
    def reserve(self,id,case,thread,model,milestone,pricing,amount,owner):
        if type(amount)is not int or amount<=0:raise SpendError('INVALID_RESERVATION')
        with self.transaction() as db:
            if db.execute('SELECT count(*) FROM holds').fetchone()[0]:raise SpendError('LEDGER_RECONCILIATION_REQUIRED')
            session=db.execute('SELECT * FROM sessions WHERE owner=?',(owner,)).fetchone()
            if not session or (session['case_id'],session['thread'])!=(case,thread):raise SpendError('LIVE_SESSION_REQUIRED')
            if db.execute('SELECT id FROM requests WHERE id=?',(id,)).fetchone():raise SpendError('REQUEST_ALREADY_RESERVED; reconcile, never blindly rebill')
            cap=db.execute('SELECT cap FROM cases WHERE id=?',(case,)).fetchone()
            if not cap:raise SpendError('CASE_ALLOCATION_REQUIRED')
            for scope,total,limit in [('project',self.spent(db),db.execute('SELECT project_cap FROM config').fetchone()[0]),('case:'+case,self.spent(db,case),cap[0])]:
                if total+amount>limit:raise SpendError('PROJECT_SPENDING_CAP' if scope=='project' else 'INVESTIGATION_SPENDING_CAP')
                for threshold in [50,80,95,100]:
                    if (total+amount)*100>=limit*threshold:db.execute('INSERT OR IGNORE INTO warnings VALUES(?,?,?)',(scope,threshold,time.time()))
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
                status='SETTLED_OVER_RESERVATION';db.execute('INSERT OR REPLACE INTO holds VALUES(1,?)',('Provider usage exceeded conservative reservation; review pricing and limits',))
            db.execute('UPDATE requests SET charged=?,status=?,usage=?,error=? WHERE id=?',(actual,status,encoded,category,id))
    def summary(self,case=None):
        with self.db() as db:
            cap=db.execute('SELECT project_cap FROM config').fetchone()[0];total=self.spent(db)
            case_row=db.execute('SELECT cap FROM cases WHERE id=?',(case,)).fetchone() if case else None
            return {'currency':'USD','unit':'nanodollars','project_cap':cap,'project_accounted':total,'project_remaining':max(0,cap-total),
                'case_cap':case_row[0] if case_row else None,'case_accounted':self.spent(db,case) if case else None,
                'uncertain_requests':db.execute("SELECT count(*) FROM requests WHERE status!='SETTLED'").fetchone()[0],
                'holds':[dict(row) for row in db.execute('SELECT * FROM holds')],'sessions':[dict(row) for row in db.execute('SELECT * FROM sessions')],
                'warnings':[dict(row) for row in db.execute('SELECT * FROM warnings ORDER BY scope,threshold')],
                'accounting_scope':'Managed requests since B10-O; historical/external billing unknown; not a Google hard cap'}

    def update_limits(self,*,reason,project_limit=None,default_case_limit=None,max_concurrent=None):
        if not isinstance(reason,str) or not reason.strip():raise SpendError('OPERATOR_REASON_REQUIRED')
        with self.transaction() as db:
            if db.execute('SELECT count(*) FROM sessions').fetchone()[0]:raise SpendError('STOP_LIVE_SESSIONS_BEFORE_CONFIG_CHANGE')
            old=dict(db.execute('SELECT * FROM config WHERE id=1').fetchone());new=dict(old)
            if project_limit is not None:new['project_cap']=dollars(project_limit)
            if default_case_limit is not None:new['case_cap']=dollars(default_case_limit)
            if max_concurrent is not None:
                if type(max_concurrent)is not int or not 1<=max_concurrent<=4:raise SpendError('INVALID_CONCURRENCY_LIMIT')
                new['max_concurrent']=max_concurrent
            if new['project_cap']<self.spent(db) or new['case_cap']>new['project_cap']:raise SpendError('LIMIT_BELOW_ACCOUNTED_USAGE')
            db.execute('UPDATE config SET project_cap=?,case_cap=?,max_concurrent=? WHERE id=1',(new['project_cap'],new['case_cap'],new['max_concurrent']))
            db.execute('INSERT INTO config_changes(previous,current,reason,created) VALUES(?,?,?,?)',(json.dumps(old),json.dumps(new),reason,time.time()))

if __name__=='__main__':
    print(json.dumps(Ledger().summary(),indent=2))
