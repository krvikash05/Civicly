"""Read-only old witness + upgraded COPY and new durable simulated accounting probe."""
import argparse,hashlib,json,os,sqlite3
from pathlib import Path
from app.active import ROOT
from app.agents.spending import Ledger,Pricing,dollars

TABLES=['config','cases','requests','holds','config_changes','warnings','sessions']
def rows(path,tables):
    with sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        return {t:[dict(r) for r in db.execute('SELECT * FROM '+t+' ORDER BY 1')] for t in tables}
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['create','verify']);p.add_argument('--output',required=True);p.add_argument('--anchor');a=p.parse_args()
    old=ROOT/'.runtime/b10o-spending-probe.sqlite3';before=rows(old,TABLES)
    original=json.loads((ROOT/'docs/evidence/B10O-spending-before.json').read_text())['tables']
    assert before==original,'Original accounting witness changed'
    target=ROOT/'.runtime/b10or-spending-probe.sqlite3';copy=ROOT/'.runtime/b10or-legacy-copy.sqlite3'
    if a.mode=='create':
        if target.exists() or copy.exists():raise RuntimeError('Existing probe: never erase; verify instead')
        with sqlite3.connect('file:'+str(old)+'?mode=ro',uri=True) as src,sqlite3.connect(copy) as dst:src.backup(dst)
        copy.chmod(0o600);upgraded=Ledger(copy)
        after=rows(copy,TABLES)
        assert [{k:v for k,v in row.items() if k!='complex_cap'} for row in after['config']]==before['config']
        assert all(after[t]==before[t] for t in TABLES if t!='config')
        upgraded.update_limits(reason='Synthetic operator approved8/.50 on COPY only',project_limit=8,default_case_limit='.50',complex_case_limit='1.50')
        assert rows(copy,['requests'])['requests']==before['requests']
        l=Ledger(target);l.configure_case('B10OR-PROBE');l.acquire('B10OR-PROBE','T','O');tariff=Pricing();usage={'promptTokenCount':100,'candidatesTokenCount':20,'totalTokenCount':120}
        for id in ['UNKNOWN','OVER']:
            l.reserve(id,'B10OR-PROBE','T',tariff.data['model'],'B10OR-SIMULATED',tariff.version,1000,'O',token_reservation=5000,token_limit=60000)
            l.reconcile(id,None if id=='UNKNOWN' else tariff.actual(usage),{} if id=='UNKNOWN' else usage)
        l.release('O');info=l.inspect_hold('OVER')
        l.resolve_hold('OVER',authorized=True,operator='synthetic-operator',reason='Bound simulated usage and tariff; caps sufficient',verified_pricing=tariff.version,usage_sha256=hashlib.sha256(info['request']['usage'].encode()).hexdigest(),evidence_ref='SIMULATED-RECEIPT')
    value={'mode':'SIMULATED_ACCOUNTING_NO_PROVIDER','original_B10O_witness_unchanged':rows(old,TABLES)==before,'original_caps':before['config'],'upgraded_copy':rows(copy,TABLES+['accounting_events']),'new_probe':rows(target,TABLES+['request_holds','accounting_events','token_usage','token_floors']),'thread_accounted_tokens':Ledger(target).thread_tokens('T'),'actual_external_provider_requests':0}
    assert value['thread_accounted_tokens']==5120
    if a.mode=='verify':assert value==json.loads(Path(a.anchor).read_text()),'Probe changed after lifecycle'
    Path(a.output).write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':'PASS','mode':a.mode,'original_history_unchanged':True,'durable_token_exposure':5120,'actual_provider_requests':0}))
if __name__=='__main__':main()
