"""Trusted local operator credential bootstrap; never an agent/MCP tool."""
import argparse,json,os,secrets
from pathlib import Path
from .auth import Auth,OPERATORS

def main():
 p=argparse.ArgumentParser();p.add_argument('operation',choices=['configure']);p.add_argument('--directory',type=Path,default=Path('.runtime/auth'));a=p.parse_args()
 a.directory.mkdir(parents=True,exist_ok=True);a.directory.chmod(0o700)
 passwords={id:secrets.token_urlsafe(32) for id in OPERATORS}
 db=a.directory/'auth.sqlite3';credentials=a.directory/'credentials.json'
 if db.exists() or credentials.exists():raise SystemExit('Existing auth files retained; explicit operator review required')
 Auth.provision(db,passwords)
 fd=os.open(credentials,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as out:json.dump(passwords,out)
 print('Configured private demo authentication; credentials remain in the owner-only runtime directory. No values displayed.')
if __name__=='__main__':main()
