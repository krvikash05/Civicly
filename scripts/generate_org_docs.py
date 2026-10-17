#!/usr/bin/env python3
"""Create source-attributed *synthetic* municipal operations documents for GraphRAG experiments."""
import json,pathlib,hashlib
root=pathlib.Path(__file__).resolve().parents[1]
dir=root/'data/documents';dir.mkdir(exist_ok=True)
rows=[
 ('D001','Drainage Operations','Drain blockage inspection','Before recommending drain cleaning, verify upstream inlet and downstream segment; log debris depth, flow direction, source, photos and date. Do not infer obstruction from nearby litter alone.'),
 ('D002','Drainage Operations','Drain capacity and storm comparison','Compare rainfall accumulation and time period against recorded drain capacity. A clear drain can still be undersized. Exceptional rain does not establish routine blockage.'),
 ('D003','Drainage Operations','Pumping station safety','Inspect pump status, backup power and downstream discharge constraints. A failed pump requires authorized maintenance and safety controls.'),
 ('D004','Road Maintenance','Recurring pothole inspection','When potholes return after a surface patch, inspect water infiltration, subgrade, drainage and prior materials before proposing repeated patching.'),
 ('D005','Water Utilities','Underground pipe leakage','Pipe proximity to road damage is not proof of leakage. Verify pressure/leak findings and repair approval before excavation.'),
 ('D006','Road Maintenance','Utility-road restoration dependencies','Utility line inspection and stabilization should precede final road restoration when excavation or active leakage is verified. Exceptions require recorded approval.'),
 ('D007','Sanitation Services','Collection point capacity','Compare recorded pickup execution, expected waste generation and nominal bin capacity. Overflow after a missed route differs from unauthorized dumping.'),
 ('D008','Sanitation Services','Pickup route execution','A scheduled pickup is not proof of collection. Use signed actual pickup logs and report MISSED or PARTIAL truthfully.'),
 ('D009','Sanitation Services','Recurring dumping response','When collections are on time but waste reappears outside designated sites, request observation of disposal behavior and appropriate public-space measures.'),
 ('D010','Civic Operations Coordination','Approval boundaries','A plan is a proposal until an authorized approver validates the exact plan version and immutable content hash. AI recommendations cannot self-authorize work.'),
 ('D011','Civic Operations Coordination','Resolution versus completion','An assigned task may be completed while the underlying civic problem remains unresolved. Track recurrence criteria separately.'),
 ('D012','Drainage Operations','Follow-up waterlogging verification','After drainage work, monitor comparable rainfall conditions before verifying recurrent waterlogging as resolved.'),
 ('D013','Road Maintenance','Follow-up pavement inspection','Track surface and structural condition after remedial work; do not mark permanent road recovery from contractor completion alone.'),
 ('D014','Sanitation Services','Follow-up service adequacy','Require multiple scheduled pickup observations and absence of renewed accumulation before declaring collection problems resolved.'),
 ('D015','Civic Operations Coordination','Cross-department sequencing','Tasks depend on affected infrastructure, findings and safety. Waste removal, drainage inspection and road restoration order is case-dependent.'),
 ('D016','Civic Operations Coordination','Historical investigation memorandum','Past Market Junction cleaning improved short-term drainage but did not establish downstream capacity. Future investigations should request downstream inspection.'),
 ('D017','Water Utilities','Normal pressure does not prove all foundations sound','A passed pipe pressure test reduces support for an active utility leak but does not directly diagnose pavement subgrade.'),
 ('D018','Civic Operations Coordination','Data provenance and uncertainty','All reports are claims until corroborated; AI-extracted document relationships remain candidate and require source attribution and review.'),
]
manifest=[]
for doc_id,owner,title,body in rows:
 fn=f'{doc_id}_{title.lower().replace(" ","_")}.md'
 txt=f'# {title}\n\n**DOCUMENT ID:** {doc_id}\n**SOURCE KIND:** SYNTHETIC\n**ORGANIZATION:** Fictional Civicly Demo City\n**OWNER:** {owner}\n**VERSION:** 1\n**EFFECTIVE FROM:** 2026-09-01\n\n## Procedure / lesson\n\n{body}\n\nThese are invented demonstration records and do not claim to be official policies of any real municipality.\n'
 p=dir/fn;p.write_text(txt)
 manifest.append({'document_id':doc_id,'title':title,'owner_department_name':owner,'source_kind':'SYNTHETIC','synthetic':True,'effective_from':'2026-09-01','version':1,'file_path':f'data/documents/{fn}','sha256':hashlib.sha256(txt.encode()).hexdigest(),'status':'ACTIVE'})
(root/'data/documents/manifest.json').write_text(json.dumps({'version':1,'documents':manifest},indent=2)+'\n')
print('Created',len(rows),'synthetic organization documents')
