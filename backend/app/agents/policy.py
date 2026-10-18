"""Invocation-bound permission. Credential presence never authorizes a live request."""
from dataclasses import dataclass
import os
from uuid import uuid4

class LiveDenied(RuntimeError):pass

@dataclass(frozen=True)
class Permit:
    investigation_id:str
    thread_id:str
    milestone:str='B10'
    max_usd:str|None=None
    mode:str='LIVE'
    @classmethod
    def explicit_live(cls,*,approved,investigation_id,thread_id,max_usd=None,milestone='B10'):
        if approved is not True or not investigation_id or not thread_id:raise LiveDenied('EXPLICIT_INVOCATION_OPT_IN_REQUIRED')
        return cls(investigation_id,thread_id,milestone,None if max_usd is None else str(max_usd),'LIVE')
    @classmethod
    def mocked(cls,investigation_id='TEST_INV',thread_id=None):
        return cls(investigation_id,thread_id or uuid4().hex,'B10-O-TEST','.15','MOCK_HTTP')
    @property
    def case_key(self):return self.investigation_id
    def check(self,transport,context):
        import httpx
        if self.mode=='MOCK_HTTP':
            if not isinstance(transport,httpx.MockTransport):raise LiveDenied('MOCK_PERMIT_REQUIRES_MOCK_TRANSPORT')
            return
        if self.mode!='LIVE' or os.environ.get('CIVICLY_TEST_NO_LIVE')=='1':raise LiveDenied('LIVE_PROVIDER_DISABLED_IN_ORDINARY_TESTS')
        state=context.get('state',{})
        if state.get('investigation_id')!=self.investigation_id or state.get('thread_id')!=self.thread_id:raise LiveDenied('LIVE_INVOCATION_SCOPE_MISMATCH')
