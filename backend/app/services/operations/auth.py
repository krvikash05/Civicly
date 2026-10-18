"""Local demo identities and signed revocable sessions; no caller roles trusted."""
import hashlib,hmac,json,os,secrets,sqlite3,time,re
from contextlib import contextmanager
from pathlib import Path
from app.services.evidence.models import Actor
class Denied(ValueError):pass
OPERATORS={
 'OP-ANALYST':('ANALYST','DEPT-COORD'), 'OP-APPROVER':('APPROVER','DEPT-COORD'),
 'OP-DRAIN-LEAD':('DEPARTMENT_LEAD','DEPT-DRAIN'), 'OP-ROAD-LEAD':('DEPARTMENT_LEAD','DEPT-ROAD'),
 'OP-WASTE-LEAD':('DEPARTMENT_LEAD','DEPT-SAN'), 'OP-WATER-LEAD':('DEPARTMENT_LEAD','DEPT-WATER'), 'OP-ADMIN':('ADMIN','DEPT-COORD')}
PERMISSIONS={'draft':{'ANALYST'},'submit':{'ANALYST'},'decide':{'APPROVER'},'order':{'APPROVER'},'update':{'DEPARTMENT_LEAD'},'read':{'ANALYST','APPROVER','DEPARTMENT_LEAD','ADMIN'},'revoke_session':{'ADMIN'}}
PERMISSIONS.update(progress={'DEPARTMENT_LEAD'},inspect={'DEPARTMENT_LEAD','ANALYST'},evaluate={'ANALYST'},recur={'ANALYST'})
class Auth:
 def __init__(self,path,*,clock=time.time):
  self.path=Path(path);self.clock=clock
  if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_mode&0o077:raise Denied('PRIVATE_AUTH_STORE_REQUIRED')
 @contextmanager
 def db(self):
  if self.path.is_symlink() or self.path.stat().st_mode&0o077:raise Denied('PRIVATE_AUTH_STORE_REQUIRED')
  db=sqlite3.connect(self.path);db.row_factory=sqlite3.Row
  try:
   with db:yield db
  finally:db.close()
 @classmethod
 def provision(cls,path,passwords,*,clock=time.time):
  path=Path(path)
  if set(passwords)!=set(OPERATORS) or any(not isinstance(v,str) or not 16<=len(v)<=256 for v in passwords.values()):raise Denied('SEED_CREDENTIALS_INVALID')
  path.parent.mkdir(parents=True,exist_ok=True)
  fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
  with sqlite3.connect(path) as db:
   db.executescript('CREATE TABLE operator(id TEXT PRIMARY KEY,role TEXT,department TEXT,salt BLOB,password BLOB,enabled INTEGER); CREATE TABLE session(id TEXT PRIMARY KEY,operator TEXT,expires REAL,revoked INTEGER); CREATE TABLE meta(secret BLOB); CREATE TABLE audit(actor TEXT,action TEXT,subject TEXT,at REAL);')
   db.execute('INSERT INTO meta VALUES (?)',(secrets.token_bytes(32),))
   for id,(role,dept) in OPERATORS.items():
    salt=secrets.token_bytes(16);pw=hashlib.pbkdf2_hmac('sha256',passwords[id].encode(),salt,600000)
    db.execute('INSERT INTO operator VALUES (?,?,?,?,?,1)',(id,role,dept,salt,pw))
  return cls(path,clock=clock)
 def operator(self,id):
  with self.db() as db:row=db.execute('SELECT * FROM operator WHERE id=?',(id,)).fetchone()
  if not row or not row['enabled'] or (row['role'],row['department'])!=OPERATORS.get(id):raise Denied('AUTHENTICATION_REQUIRED')
  return Actor(id=id,role=row['role'],department_id=row['department'])
 def login(self,id,password):
  if not isinstance(id,str) or id not in OPERATORS or not isinstance(password,str) or not 1<=len(password)<=256:raise Denied('AUTHENTICATION_REQUIRED')
  with self.db() as db:
   row=db.execute('SELECT * FROM operator WHERE id=?',(id,)).fetchone()
   salt=row['salt'] if row else b'\0'*16
   actual=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,600000)
   if not row or not hmac.compare_digest(actual,row['password']):raise Denied('AUTHENTICATION_REQUIRED')
   self.operator(id);nonce=secrets.token_urlsafe(32);mac=hmac.new(db.execute('SELECT secret FROM meta').fetchone()[0],nonce.encode(),'sha256').hexdigest()
   token=nonce+'.'+mac;key=hashlib.sha256(token.encode()).hexdigest()
   db.execute('INSERT INTO session VALUES (?,?,?,0)',(key,id,self.clock()+1800));db.execute('INSERT INTO audit VALUES (?,?,?,?)',(id,'LOGIN',key,self.clock()))
  return token
 def resolve(self,token):
  if not isinstance(token,str) or not re.fullmatch(r'[A-Za-z0-9_-]{43}\.[0-9a-f]{64}',token):raise Denied('AUTHENTICATION_REQUIRED')
  pieces=token.split('.')
  if len(pieces)!=2:raise Denied('AUTHENTICATION_REQUIRED')
  with self.db() as db:
   mac=hmac.new(db.execute('SELECT secret FROM meta').fetchone()[0],pieces[0].encode(),'sha256').hexdigest()
   if not hmac.compare_digest(mac,pieces[1]):raise Denied('AUTHENTICATION_REQUIRED')
   row=db.execute('SELECT * FROM session WHERE id=?',(hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
  if not row or row['revoked'] or row['expires']<=self.clock():raise Denied('AUTHENTICATION_REQUIRED')
  return self.operator(row['operator'])
 def require(self,token,operation):
  actor=self.resolve(token)
  if actor.role not in PERMISSIONS.get(operation,set()):raise Denied('ROLE_DENIED')
  return actor
 def logout(self,token):
  actor=self.resolve(token);key=hashlib.sha256(token.encode()).hexdigest()
  with self.db() as db:db.execute('UPDATE session SET revoked=1 WHERE id=?',(key,));db.execute('INSERT INTO audit VALUES (?,?,?,?)',(actor.id,'LOGOUT',key,self.clock()))
 def revoke_session(self,admin_token,token):
  actor=self.require(admin_token,'revoke_session');key=hashlib.sha256(token.encode()).hexdigest()
  with self.db() as db:db.execute('UPDATE session SET revoked=1 WHERE id=?',(key,));db.execute('INSERT INTO audit VALUES (?,?,?,?)',(actor.id,'REVOKE_SESSION',key,self.clock()))
