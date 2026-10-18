"""B18 parsing/private-input/dispatch units; not DB or genuine model evidence."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from cli.main import parser,main,key,ACTIONS,EXIT
from cli.private import read_json,write_private,session,scope
from app.api.coverage import ROUTES
BASE=['--profile','private-profile','--auth-store','private-auth','--memory-profile','private-memory','--session','private-session']

@pytest.mark.parametrize('group,action,method,path',[(g,a,*v) for g,rows in ACTIONS.items() for a,v in rows.items()])
def test_command_exact_accepted_api_mapping(group,action,method,path):
 args=[*BASE,group,action]
 if '{id}' in path:args+=['--id','ID']
 if method=='POST':args+=['--key','K','--payload','input.json']
 parsed=parser().parse_args(args)
 assert (parsed.group,parsed.action)==(group,action)
 assert any((r[0],r[1])==(method,path) for r in ROUTES)

@pytest.mark.parametrize('extra',[['--live'],['--password','PRIVATE_VALUE'],['--graph','civicly_knowledge'],['--provider','gemini'],['advance','run','--key','K','--batches','5'],['reset','--output-dir','private','--key','K','--target','civicly_knowledge']])
def test_closed_parser_does_not_echo_private_input(extra,capsys):
 with pytest.raises(SystemExit) as error:parser().parse_args([*BASE,*extra])
 assert error.value.code==2
 value=capsys.readouterr();assert 'PRIVATE_VALUE' not in value.out+value.err
 assert json.loads(value.out)['error']['code']=='VALIDATION_ERROR'

@pytest.mark.parametrize('value',['','with space','line\nline','a'*201])
def test_mutations_require_bounded_printable_key(value):
 with pytest.raises(ValueError):key(value)

def test_private_files_and_session_exact_source(tmp_path):
 path=tmp_path/'session.json';p=SimpleNamespace(graph='SOURCE');auth=tmp_path/'auth'
 value={'version':1,'scope':scope(p,auth),'token':'PRIVATE_VALUE','operator_id':'OP','login_key':'K'}
 write_private(path,value);assert path.stat().st_mode&0o077==0
 assert session(path,p,auth)==value
 with pytest.raises(ValueError):session(path,SimpleNamespace(graph='OTHER'),auth)
 path.chmod(0o644)
 with pytest.raises(ValueError):read_json(path,private=True)
 path.chmod(0o600);link=tmp_path/'link';link.symlink_to(path)
 with pytest.raises(ValueError):read_json(link,private=True)
 with pytest.raises(FileExistsError):write_private(path,value)

@pytest.mark.parametrize('raw',['{"a":1,"a":2}','{"a":NaN}'])
def test_json_rejects_duplicate_fields_and_nonfinite(tmp_path,raw):
 path=tmp_path/'payload';path.write_text(raw)
 with pytest.raises(ValueError):read_json(path)

@pytest.mark.parametrize('command',['health','migrate','schema-status'])
def test_legacy_command_arguments_forwarded_unchanged(monkeypatch,command):
 import cli.legacy
 calls=[];monkeypatch.setattr(cli.legacy,'main',lambda argv:calls.append(argv) or 0)
 argv=[command,'--env-file','local.env']+(['--retry-failed'] if command=='migrate' else [])
 assert main(argv)==0 and calls==[argv]

@pytest.mark.parametrize('error,code', [('VALIDATION_ERROR',2),('UNAUTHORIZED',3),('PERMISSION_DENIED',3),('CONFLICT',4),('DEPENDENCY_BLOCKED',5),('RECOVERY_REQUIRED',6)])
def test_stable_exit_codes(error,code):assert EXIT[error]==code

@pytest.mark.parametrize('kind,expected',[('validation',2),('authorization',3),('conflict',4),('dependency',5),('unknown',6),('external',5)])
def test_errors_sanitized_and_unknown_ids_preserved(monkeypatch,capsys,kind,expected):
 import cli.main as cli
 from app.graph.repository import Conflict,PreconditionFailed
 from app.services.http.service import Recovery
 from app.services.operations.auth import Denied
 errors={'validation':ValueError('PRIVATE_VALUE'),'authorization':Denied('PRIVATE_VALUE'),'conflict':Conflict('PRIVATE_VALUE'),'dependency':PreconditionFailed('PRIVATE_VALUE'),'unknown':Recovery('REQUEST',identities={'investigation_id':'INV'}),'external':RuntimeError('PRIVATE_VALUE')}
 async def execute(args):raise errors[kind]
 monkeypatch.setattr(cli,'execute',execute)
 assert main([*BASE,'test'])==expected
 raw=capsys.readouterr().out;assert 'PRIVATE_VALUE' not in raw
 if kind=='unknown':assert json.loads(raw)['error']['details']=={'commitment':'UNKNOWN','request_id':'REQUEST','investigation_id':'INV'}

def test_test_command_has_no_arbitrary_shell_or_suite(capsys):
 with pytest.raises(SystemExit):parser().parse_args([*BASE,'test','--command','PRIVATE_VALUE'])
 assert 'PRIVATE_VALUE' not in capsys.readouterr().out

@pytest.mark.parametrize('mode',['unknown','conflict','done'])
def test_advance_replay_never_dispatches(monkeypatch,mode):
 import asyncio
 from contextlib import nullcontext
 from app.graph.repository import Conflict
 from app.graph.models import digest
 from app.services.http.service import Recovery
 from cli.advance import advance
 old={'hash':digest(['run',1]),'status':'DISPATCHING' if mode=='unknown' else 'DONE','receipt':{'historical':'receipt'}}
 if mode=='conflict':old['hash']='different'
 repo=SimpleNamespace(_session=lambda:nullcontext(None))
 s=SimpleNamespace(profile=SimpleNamespace(graph='SOURCE'),repo=repo,delivery=SimpleNamespace(store=SimpleNamespace(get=lambda *args:old)))
 actor=SimpleNamespace(role='ANALYST',id='OP')
 if mode=='done':assert asyncio.run(advance(s,'run',1,'KEY',actor,'private'))==old['receipt']
 else:
  with pytest.raises(Recovery if mode=='unknown' else Conflict):asyncio.run(advance(s,'run',1,'KEY',actor,'private'))


def test_explain_uses_actual_paths_and_filters_scope(monkeypatch):
 from app.services.operator import explain
 import app.services.operator as module
 from app.graph.models import PathRecord
 from app.graph.repository import PreconditionFailed
 view={'nodes':[{'id':id,'labels':['Evidence'],'kind':'Evidence','display_label':id,'status':None,'source_kind':'SYNTHETIC','evidence_ids':[],'observed_at':None} for id in ['A','B']],'edges':[{'id':'E','type':'SUPPORTED_BY','source':'A','target':'B','valid_from':None,'valid_to':None,'observed_at':None,'verification_status':'RECORDED_ASSOCIATION_NOT_CAUSATION','source_evidence_ids':['B']}],'decision_path_ids':[],'graph_revision':1,'as_of':'2026-10-18T00:00:00Z','truncated':False,'reservations':[]}
 paths=[PathRecord(node_ids=('A','B'),edge_ids=('E',),directions=('OUTGOING',),evidence_ids=('B',)),PathRecord(node_ids=('A','PRIVATE'),edge_ids=('FOREIGN',),directions=('OUTGOING',),evidence_ids=('PRIVATE',))]
 result=SimpleNamespace(graph_revision=1,paths=paths,truncated=False,search_limited=True,reservations=['Bounded context'])
 monkeypatch.setattr(module,'GraphQueries',lambda repo:SimpleNamespace(run=lambda request:result))
 output=explain(None,'INV',view,view['as_of'])
 assert len(output['analysis_paths'])==1 and 'PRIVATE' not in json.dumps(output)
 assert output['analysis_search_limited'] and output['analysis_path_kind'].endswith('NOT_MODEL_SELECTED')
 result.graph_revision=2
 with pytest.raises(PreconditionFailed):explain(None,'INV',view,view['as_of'])

@pytest.mark.parametrize('operation',['advance','reset'])
def test_uncertain_initial_intent_preserves_original_request_id(monkeypatch,tmp_path,operation):
 import asyncio
 from contextlib import nullcontext
 from app.graph.repository import OutcomeUnknown
 from app.services.http.service import Recovery
 repo=SimpleNamespace(_session=lambda:nullcontext(None))
 def fail(*args,**kw):raise OutcomeUnknown('PRIVATE_VALUE')
 s=SimpleNamespace(profile=SimpleNamespace(graph='SOURCE'),auth=SimpleNamespace(path=tmp_path/'auth'),repo=repo,delivery=SimpleNamespace(store=SimpleNamespace(get=lambda *args:None,write=fail)))
 actor=SimpleNamespace(role='ADMIN',id='OP')
 with pytest.raises(Recovery) as error:
  if operation=='advance':
   from cli.advance import advance
   asyncio.run(advance(s,'run',1,'KEY',actor,'private'))
  else:
   import cli.reset as module
   monkeypatch.setattr(module,'fixture',lambda:([],[],{}))
   module.reset(s,tmp_path/'NEW','KEY',actor)
 assert error.value.reconciliation['request_id'].startswith('CLI-B18-' if operation=='advance' else 'RESET-B18-')
 assert not (tmp_path/'NEW').exists()
