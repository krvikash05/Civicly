"""Explicit host-injected services; request inputs cannot select capabilities."""
from dataclasses import dataclass
from fastapi import Request,Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from app.services.operations.auth import Denied
class HTTPFailure(Exception):
 def __init__(self,status,code,*,details=None):self.status,self.code,self.details=status,code,details or {}
bearer=HTTPBearer(auto_error=False)
def services(request:Request):
 value=getattr(request.app.state,'services',None)
 if value is None:raise HTTPFailure(503,'EXTERNAL_UNAVAILABLE')
 return value
@dataclass
class Principal:
 actor:object
 token:str

def authenticated(creds:HTTPAuthorizationCredentials|None=Depends(bearer),s=Depends(services)):
 if creds is None or creds.scheme.lower()!='bearer':raise HTTPFailure(401,'UNAUTHORIZED')
 try:actor=s.auth.resolve(creds.credentials)
 except Denied:raise HTTPFailure(401,'UNAUTHORIZED') from None
 return Principal(actor,creds.credentials)
