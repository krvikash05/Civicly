"""TEST ONLY graph-reactive simulated Gemini transport; never a model-quality claim."""
import json
import httpx
from app.agents.provider import PROMPT
from app.agents.models import Selection
from tests.b10_fixtures import choose

class ReactiveHTTP:
    def __init__(self,selector,*,fault=None):self.selector=selector;self.fault=fault;self.contexts=[];self.calls=0
    async def __call__(self,request):
        assert request.url.path.endswith(':generateContent')
        self.calls+=1;body=json.loads(request.content)
        assert body['generationConfig']['responseJsonSchema']==Selection.model_json_schema()
        assert body['generationConfig']['thinkingConfig']=={'thinkingLevel':'LOW'}
        text=body['contents'][0]['parts'][0]['text'];assert text.startswith(PROMPT+'\nCONTEXT_JSON:\n')
        raw=text.split('\nCONTEXT_JSON:\n',1)[1].split('\nPrevious output failed strict validation.',1)[0]
        context=json.loads(raw);self.contexts.append(context)
        if self.calls==1 and self.fault:
            if self.fault=='timeout':raise httpx.ReadTimeout('SIMULATED',request=request)
            if self.fault in {'503','429','quota'}:
                code=503 if self.fault=='503' else 429
                payload={'error':{'details':[{'@type':'type.googleapis.com/google.rpc.QuotaFailure','violations':[{'quotaId':'requestsPerDay'}]}]}} if self.fault=='quota' else {}
                return httpx.Response(code,headers={'retry-after':'0'},json=payload)
            if self.fault=='invalid':return self.response({'bad':'SIMULATED_INVALID_OUTPUT'})
        selection,_=await self.selector.choose(context,context['state']['remaining']['tokens'])
        return self.response(selection.model_dump(mode='json'))
    @staticmethod
    def response(value):
        return httpx.Response(200,json={'modelVersion':'gemini-3.8-flash','usageMetadata':{'promptTokenCount':100,'candidatesTokenCount':20,'thoughtsTokenCount':10,'totalTokenCount':130},'candidates':[{'content':{'parts':[{'text':json.dumps(value)}]}}]})

class ReadPause:
    async def choose(self,c,remaining):
        s=c['state']
        last=s['observations'][-1] if s['observations'] else {}
        # Each resumed wake gets another real read, using persisted graph-backed results.
        if s['refresh_required'] or not last or last.get('host_generated') or getattr(self,'wake',None)!=s['wakes']:
            self.wake=s['wakes'];return Selection.model_validate(choose('READ',{'template':'node','id':s['incident_ids'][0]},'official::query_graph_readonly')),0
        return Selection.model_validate(choose()),0

class HistoryReactive:
    """Test selector responds to actual B09 contradiction, including CONTESTED cases."""
    async def choose(self,c,remaining):
        from tests.integration.test_agent_reasoning import EvidenceReactiveFake
        selection,used=await EvidenceReactiveFake().choose(c,remaining)
        if selection.action=='INSPECT':
            latest=c['hypotheses'][0]['assessments'][-1]
            if latest['classification']['reviewed_contradiction_ids']:
                return Selection.model_validate(choose('INSPECT',{'asset_ids':['D1'],'department_id':'DEP','inspection_type':'CAPACITY_TEST'})),used
        return selection,used
