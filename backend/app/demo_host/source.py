"""One presenter source writer at a time, including field release and live wakes."""
from contextlib import contextmanager
from .runtime import HostBlocked

@contextmanager
def source_writer(repo,seconds=360):
 lock=repo.client.connection.lock('civicly:demo-source-writer:'+repo.graph.name,timeout=seconds,blocking=False,thread_local=False)
 if not lock.acquire(blocking=False):raise HostBlocked('DEMO_SOURCE_BUSY')
 try:yield
 finally:
  if lock.owned():lock.release()
