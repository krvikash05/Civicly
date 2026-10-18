"""Fresh-process actual SDK retrieval through scoped read credential; no LLM."""
import asyncio,json,sys
from pathlib import Path
from app.memory.runtime import Profile
p=Profile.model_validate_json(Path(sys.argv[1]).read_text());db,m=p.connect()
try:
 result=asyncio.run(m.retrieve(as_of='2026-10-18T00:00:00Z',document_id=sys.argv[3] if len(sys.argv)>3 else 'D001'))
 assert result['citations']
 Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
finally:db.connection.close();db.connection.connection_pool.disconnect()
