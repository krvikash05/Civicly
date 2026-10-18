"""Public SDK saver and serialized wake ownership, with uncertain-write quarantine."""
import asyncio
from contextlib import asynccontextmanager
from langchain_falkordb.checkpoint import FalkorDBSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

class RecoveryRequired(RuntimeError):pass

def saver(profile):
    return FalkorDBSaver(host='127.0.0.1',port=6379,username=profile.checkpoint_user,
        password=profile.checkpoint_password.get_secret_value(),database=profile.checkpoints,
        serde=JsonPlusSerializer(pickle_fallback=False,allowed_json_modules=[],allowed_msgpack_modules=[]))

@asynccontextmanager
async def ownership(client,profile,thread):
    # Host-owned Redis lease, never exposed to model or checkpoint-only account.
    from app.graph.models import digest
    key='civicly:b10:'+profile.graph+':'+digest(thread)
    if client.connection.get(key+':quarantine'):raise RecoveryRequired('CHECKPOINT_QUARANTINED; operator must reconcile last public checkpoint after stopping old process')
    lock=client.connection.lock(key,timeout=90,blocking=False,thread_local=False)
    if not lock.acquire(blocking=False):raise RecoveryRequired('CONCURRENT_RESUME_DENIED')
    healthy=True
    async def heartbeat():
        nonlocal healthy
        try:
            while True:
                await asyncio.sleep(15)
                await asyncio.to_thread(lock.extend,90,replace_ttl=True)
        except asyncio.CancelledError:raise
        except Exception:healthy=False
    task=asyncio.create_task(heartbeat())
    def check():
        if client.connection.get(key+':quarantine'):raise RecoveryRequired('CHECKPOINT_QUARANTINED')
        if not healthy or not lock.owned():raise RecoveryRequired('WAKE_LEASE_LOST')
    try:yield check
    except BaseException:
        # A late vendor thread may still be writing. No automated reset or blind retry.
        client.connection.set(key+':quarantine','uncertain wake; stop old process and reconcile public checkpoint')
        raise
    finally:
        task.cancel()
        try:await task
        except asyncio.CancelledError:pass
        if lock.owned():lock.release()
