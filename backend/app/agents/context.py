"""Deterministic decision projection; full source histories remain in FalkorDB."""
import copy,json
from app.graph.models import digest

TRANSPORT={'context','trace_id','execution_id','server_id','tool_name','schema_version','inventory_version','simulation_mode'}

def unique(values):
    seen=set();result=[]
    for v in values:
        h=digest(v)
        if h not in seen:seen.add(h);result.append(v)
    return result

def assessment(value):
    # Latest assessment is authoritative; reports are source facts, never LLM summaries.
    return copy.deepcopy(value)

def historical_material(history):
    # Every prior supporting/contrary/context/exclusion classification and proof remains.
    keys=['id','hypothesis_id','graph','cause_code','mechanism','confirming_codes','falsifying_codes','state_transitions','previous_assessment_id','assessment','rule_version','format_version','assessed_at','as_of','graph_revision','source_graph_revision',
          'supporting_evidence_ids','contradicting_evidence_ids','excluded_evidence_ids','classification','paths','path_ids','missing_evidence','reservations','search_limited','truncated']
    return [{k:a[k] for k in keys if k in a} | {'evidence_references':copy.deepcopy(a.get('evidence_references',[]))} for a in history]

def observation(value):
    if value.get('operation') in {'assess','propose','request_inspection'}:
        # Assessment body is included once under its hypothesis, not in every receipt.
        return {k:v for k,v in value.items() if k!='assessment'}
    return {k:v for k,v in value.items() if k not in TRANSPORT}

def build(state,hypotheses,catalog,policies,action_schemas,departments,spending=None):
    s=state.model_dump(mode='json');raw=s.pop('observations');facts={};material=[]
    def list_records(value):
        # Domain histories also carry typed records outside data.nodes/edges/paths.
        # Intern those complete records, retaining every field and original order.
        if isinstance(value,list):
            out=[]
            for item in value:
                if isinstance(item,dict):
                    ref=digest(item);facts[ref]=copy.deepcopy(item);out.append({'fact_ref':ref})
                else:out.append(list_records(item))
            return out
        if isinstance(value,dict):return {k:list_records(v) for k,v in value.items()}
        return value
    # Intern repeated source records by full-content hash, so different versions never merge.
    for index,item in enumerate(raw):
        row=observation(item);data=dict(row.pop('data',{}));refs={}
        for kind in ['nodes','edges','paths']:
            refs[kind]=[]
            for fact in data.pop(kind,[]):
                key=digest(fact);facts[key]=fact;refs[kind].append(key)
        material.append({'result':list_records(row),'data':list_records(data),'fact_refs':refs,'source_observation_index':index})
    # Model test/role adapters retain the recent observation shape. No transcript/logs.
    s['observations']=[observation(v) for v in raw[-2:]]
    for key in ['nodes','decisions','executions','evidence','budget']:
        s.pop(key,None)
    s['last_decision_id']=state.decisions[-1] if state.decisions else None
    s['remaining']={'iterations':max(0,state.budget.max_iterations-state.iterations),'tools':max(0,state.budget.max_tools-state.tool_calls),'tokens':max(0,state.budget.max_tokens-state.tokens),'max_seconds':state.budget.max_seconds,'wakes':max(0,state.budget.max_wakes-state.wakes)}
    # Reports referenced by several assessment versions are transmitted once, intact.
    def intern_reports(value):
        if isinstance(value,dict):
            out={}
            for key,item in value.items():
                if key=='report' and isinstance(item,dict):
                    ref=digest(item);facts[ref]=item;out[key]={'fact_ref':ref}
                else:out[key]=intern_reports(item)
            return out
        if isinstance(value,list):return [intern_reports(v) for v in value]
        return value
    schemas={};tools=[]
    for tool in catalog:
        shape=tool['input_schema'];id=digest(shape);schemas[id]=shape
        tools.append({'name':tool['name'],'description':tool['description'],'input_schema_ref':id})
    hs=[]
    for h in hypotheses:
        history=h['assessments'];latest=history[-1:]
        hs.append({'id':h['id'],'definition':h['definition'],'assessments':[assessment(v) for v in latest],
            'history_references':[{'id':v['id'],'assessment':v['assessment'],'assessed_at':v['assessed_at'],'graph_revision':v['graph_revision']} for v in history],
            'historical_material':historical_material(history[:-1])})
    return {'context_version':'B10-O-1','state':s,'hypotheses':intern_reports(hs),'catalog':tools,'tool_schemas':schemas,
        'policies':policies,'controlled_action_schemas':action_schemas,'departments':departments,
        'material_observations':unique(material),'facts':facts,'source_evidence_hashes':state.evidence,
        'spending':spending,'budget_notice':'All negatives are bounded; preserve authority/episode/temporal restrictions. A cache reference is not another tool call. Full histories remain in FalkorDB; use targeted approved retrieval or report unavailable evidence.'}
