"""Scoped Python file guard for evaluator/world artifacts, not an OS sandbox.

Agents have no filesystem tool. This additionally blocks accidental Python reads
inside agent and domain MCP execution, without hiding world data from controller.
"""
import os,sys
from pathlib import Path
from contextvars import ContextVar
from contextlib import contextmanager
ROOT=Path(__file__).resolve().parents[3]
ACTIVE=ContextVar('civicly_agent_world_isolation',default=False)
_INSTALLED=False
DIRECTORIES=tuple(ROOT/p for p in ['data/scenarios','contracts/scenarios','docs/demo','docs/evidence'])
FILES={ROOT/'contracts/demo_scenarios.json'}
def audit(event,args):
 if event!='open' or not ACTIVE.get() or not args or isinstance(args[0],int):return
 raw=args[0]
 if not isinstance(raw,(str,bytes,os.PathLike)):return
 path=Path(os.fsdecode(raw)).resolve()
 if path.name=='world.json' or path in FILES or any(path==d or d in path.parents for d in DIRECTORIES):raise PermissionError('EVALUATOR_ARTIFACT_UNAVAILABLE')
@contextmanager
def agent_files():
 global _INSTALLED
 if not _INSTALLED:sys.addaudithook(audit);_INSTALLED=True
 token=ACTIVE.set(True)
 try:yield
 finally:ACTIVE.reset(token)
