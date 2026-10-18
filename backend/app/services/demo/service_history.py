"""Controller-only authored service facts. Never imported by MCP/agents/read paths."""
import json
from datetime import timedelta
from pathlib import Path
from app.graph.schema import timestamp
from app.services.service_evidence import ServiceRecord,ServiceEvidence
from app.services.operations.service import stable

def release(services,scenario,variant,case,report_id,field,reviewer,request):
 packets=json.loads((Path(__file__).resolve().parents[4]/'data/scenarios/service-evidence-v1.json').read_text())
 packet=packets['scenarios'][scenario][variant];at=services.clock()
 def when(seconds):return (timestamp(at)-timedelta(seconds=seconds)).isoformat(timespec='microseconds').replace('+00:00','Z')
 record=ServiceRecord(id=stable('SERVICE-SOURCE',request),pickup_id=stable('PICKUP',request) if packet['status']!='UNKNOWN' else None,report_evidence_id=report_id,investigation_id=case['investigation_id'],incident_id=case['incident_id'],target_id=case['asset_id'],route_id='ROUTE-C03',scheduled_at=when(120),checked_at=when(60),actual_at=when(60) if packet['status']=='COMPLETED' else None,recorded_at=at,status=packet['status'],record_id=scenario+':'+case['investigation_id']+':service-v1',observed_by=field.id,reviewed_by=reviewer.id)
 return ServiceEvidence(services).record(record,request)
