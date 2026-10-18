"""Simulated private spending witness; never calls a model or stores credentials."""
import argparse,json
from pathlib import Path
from app.active import ROOT
from app.agents.spending import Ledger,dollars


def snapshot(ledger):
    with ledger.db() as db:
        rows={table:[dict(row) for row in db.execute('SELECT * FROM '+table+' ORDER BY 1')] for table in ['config','cases','requests','holds','config_changes','warnings','sessions']}
    return {'mode':'SIMULATED_COST_NO_PROVIDER','tables':rows,'summary':ledger.summary('B10O-DURABILITY-PROBE'),'ledger_is_separate_private_accounting':True}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['create','verify']);parser.add_argument('--anchor',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    path=ROOT/'.runtime/b10o-spending-probe.sqlite3'
    if args.mode=='create':
        if path.exists():raise RuntimeError('Probe exists; use verify, never erase accounting')
        l=Ledger(path);l.configure_case('B10O-DURABILITY-PROBE');l.acquire('B10O-DURABILITY-PROBE','T','PROBE')
        for id in ['UNKNOWN','SETTLED']:
            l.reserve(id,'B10O-DURABILITY-PROBE','T','gemini-3.8-flash','B10-O-SIMULATED','SIMULATED',dollars('.02'),'PROBE')
        l.reconcile('UNKNOWN',None,{},'SIMULATED_NETWORK_TIMEOUT');l.reconcile('SETTLED',dollars('.001'),{'simulation':True});l.release('PROBE')
        value=snapshot(l)
    else:
        if not path.exists():raise RuntimeError('Durable ledger missing')
        value=snapshot(Ledger(path));old=json.loads(Path(args.anchor).read_text());assert value==old,'Accounting changed after process/container lifecycle'
        value['matches_before_lifecycle']=True
    Path(args.output).write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':'PASS','mode':args.mode,'actual_provider_requests':0}))
if __name__=='__main__':main()
