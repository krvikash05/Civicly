"""B15 static contract parity only; no claim of runtime or delivery verification."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.events.models import Event,TYPES,route,public,backoff
c=json.loads((ROOT/'contracts/event_delivery.json').read_text())
assert c['event_schema']==Event.model_json_schema()
assert set(c['routing_defaults'])==set(TYPES)
for typ in TYPES:
 e=Event(id='EXAMPLE',type=typ,entity_id='INV',aggregate_revision=1,occurred_at='2026-10-18T00:00:00Z',payload_schema_version=1,source_kind='SYNTHETIC',idempotency_key='EXAMPLE',actor_id='operator',actor_role='SYSTEM',payload={k:'VALUE' for k in c['public_payload_allowlist']})
 assert c['routing_defaults'][typ]=={'bound_case':list(route(e,'INV')),'unbound_case':list(route(e,None))}
 assert set(public(e,'INV',1,'native:EXAMPLE'))==set(c['public_projection'])
 assert set(public(e,'INV',1,'native:EXAMPLE')['payload'])==set(c['public_payload_allowlist'])
assert [backoff(i) for i in range(1,9)]==[1,2,4,8,16,32,60,60]
assert c['municipality_scope']=={'field':'municipality_id','value':'demo-city'}
assert c['no_live_provider'] and c['b15_service_has_no_http_transport'] and not c['no_http_sse'] and c['no_automatic_quarantine_clearance']
from app.services.http.stream import EVENT_NAMES
assert c['b17_transport']['event_names']==EVENT_NAMES and set(EVENT_NAMES)==set(TYPES)
print('PASS B15 STATIC: strict event schema,20-type handler matrix, bounded public redaction/cursor contract plus B17 typed read-only SSE mapping; not runtime/ACID/provider proof')
