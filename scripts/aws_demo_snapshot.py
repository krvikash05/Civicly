"""Private, fresh-target-only presenter migration. Never emits credentials or key values."""
import argparse, hashlib, json, os, shlex, shutil, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def private_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as out:
        out.write(data)

def export(destination, host_path):
    from app.config import Settings
    from app.graph.connection import connect
    from app.graph.repository import GraphRepository
    from app.demo_host.source import source_writer
    from app.demo_host.config import load
    from app.active import load as active_load
    from app.mcp.civicly.runtime import load_config
    from app.mcp.runtime import CITY_GRAPH
    host_path = host_path.resolve()
    host = load(host_path)
    profile = active_load(host.profile)
    memory = json.loads(Path(host.memory_profile).read_text())
    trace = load_config()
    graphs = [profile.graph, profile.checkpoints, memory['canonical_graph'], memory['docs_graph'], trace['trace_graph'], CITY_GRAPH]
    users = [profile.read_user, profile.checkpoint_user, memory['reader_user'], 'civicly_mcp_b06', 'civicly_mcp_trace_b07']
    if destination.exists():
        raise ValueError('FRESH_SNAPSHOT_DIRECTORY_REQUIRED')
    destination.mkdir(parents=True, mode=0o700)
    import redis
    settings = Settings(_env_file=ROOT / '.env')
    with connect(settings) as db:
        r = redis.Redis(host=settings.host, port=settings.port, username=settings.username or None, password=settings.password.get_secret_value() if settings.password else None, decode_responses=False, socket_timeout=30)
        repo = GraphRepository(db, profile.graph)
        with source_writer(repo, 120):
            keys = {g.encode() for g in graphs if r.exists(g)}
            for graph in graphs:
                for key in r.scan_iter(match='*' + graph + '*', count=100):
                    # Copy durable quarantine/ownership markers, never an active lock.
                    name = key.decode()
                    if name == 'civicly:demo-source-writer:' + profile.graph:
                        continue
                    if name.startswith('civicly:repository-lock:'):
                        if r.pttl(key) > 0:
                            raise ValueError('SOURCE_REPOSITORY_BUSY')
                        continue
                    if name.startswith('civicly:b10:') and not name.endswith(':quarantine') and r.pttl(key) > 0:
                        raise ValueError('SOURCE_AGENT_BUSY')
                    keys.add(key)
            if len(keys) > 500:
                raise ValueError('SNAPSHOT_KEY_BOUND_EXCEEDED')
            pipe = r.pipeline(transaction=True)
            for key in sorted(keys):
                pipe.dump(key)
                pipe.pttl(key)
            values = pipe.execute()
            rows = []
            for index, key in enumerate(sorted(keys)):
                dump, ttl = values[index * 2:index * 2 + 2]
                if dump is None:
                    raise ValueError('SOURCE_CHANGED_DURING_SNAPSHOT')
                filename = f'keys/{index:04d}.dump'
                private_write(destination / filename, dump)
                rows.append({'key':key.decode(), 'file':filename, 'sha256':hashlib.sha256(dump).hexdigest(), 'ttl_ms':ttl})
            acl = []
            for line in r.acl_list():
                if shlex.split(line)[1] in users:
                    acl.append(line)
            if len(acl) != len(users):
                raise ValueError('EXPECTED_ACL_MISSING')
            private_write(destination / 'acl.json', json.dumps(acl).encode())
            # These are local private configurations, never part of a public artifact.
            presenter = Path(host_path).parent
            relative = presenter.relative_to(ROOT)
            target = destination / relative
            shutil.copytree(presenter, target)
            for name in ['ai-spend.sqlite3', 'civicly-mcp.json', 'mcp-credentials.json']:
                source = ROOT / '.runtime' / name
                dest = destination / '.runtime' / name
                dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                if source.suffix == '.sqlite3':
                    with sqlite3.connect(f'file:{source}?mode=ro', uri=True) as original, sqlite3.connect(dest) as copied:
                        original.backup(copied)
                else:
                    shutil.copy2(source, dest)
            # Back up the live authentication DB consistently, rather than copying WAL state.
            dest_auth = destination / Path(host.auth_store).relative_to(ROOT)
            with sqlite3.connect(f'file:{host.auth_store}?mode=ro', uri=True) as original, sqlite3.connect(dest_auth) as copied:
                original.backup(copied)
            aws_host = host.model_dump(mode='json')
            for field in ['profile', 'memory_profile', 'auth_store']:
                aws_host[field] = str(Path('/opt/civicly') / Path(aws_host[field]).relative_to(ROOT))
            private_write(destination / '.runtime/aws-host.json', json.dumps(aws_host).encode())
            shutil.copy2(ROOT / '.env', destination / '.env')
            private_write(destination / 'frontend/.env.local', (ROOT / 'frontend/.env.local').read_bytes())
            private_write(destination / 'manifest.json', json.dumps({'version':1,'graphs':graphs,'keys':rows,'host':'.runtime/aws-host.json'}).encode())
    for path in destination.rglob('*'):
        if path.is_file(): path.chmod(0o600)
        elif path.is_dir(): path.chmod(0o700)
    print(json.dumps({'status':'PRIVATE_SNAPSHOT_EXPORTED','graph_count':len(graphs),'key_count':len(rows),'credential_values_logged':False}))

def restore(directory, port):
    import redis
    r = redis.Redis(host='127.0.0.1', port=port, socket_timeout=30)
    if r.dbsize() != 0:
        raise ValueError('RESTORE_REQUIRES_EMPTY_DATABASE')
    manifest = json.loads((directory / 'manifest.json').read_text())
    # Validate the entire bundle before making any target writes.
    dumps = []
    for row in manifest['keys']:
        path = (directory / row['file']).resolve()
        if not path.is_relative_to(directory.resolve()): raise ValueError('INVALID_DUMP_PATH')
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != row['sha256']: raise ValueError('SNAPSHOT_HASH_MISMATCH')
        dumps.append((row,payload))
    for row, payload in dumps:
        r.restore(row['key'], max(0,row['ttl_ms']), payload, replace=False)
    for line in json.loads((directory / 'acl.json').read_text()):
        parts = shlex.split(line)
        if parts[0] != 'user' or parts[1] == 'default': raise ValueError('INVALID_ACL')
        r.execute_command('ACL','SETUSER',parts[1],'reset',*parts[2:])
    for graph in manifest['graphs']:
        if not r.exists(graph): raise ValueError('RESTORED_GRAPH_MISSING')
    print(json.dumps({'status':'RESTORED','key_count':r.dbsize(),'graph_count':len(manifest['graphs']),'credential_values_logged':False}))

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='operation',required=True)
    e = sub.add_parser('export'); e.add_argument('--destination',type=Path,required=True);e.add_argument('--host-config',type=Path,required=True)
    i = sub.add_parser('restore');i.add_argument('--directory',type=Path,required=True);i.add_argument('--port',type=int,default=6379)
    args = p.parse_args()
    if args.operation == 'export': export(args.destination,args.host_config)
    else: restore(args.directory,args.port)
