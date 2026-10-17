"""Strict report contracts. Source claims are never verified observations."""
from datetime import datetime,timezone
from decimal import Decimal
from typing import Annotated,Literal
import json,re,unicodedata,math
from pydantic import BaseModel,ConfigDict,Field,TypeAdapter,AfterValidator,field_validator,model_validator,JsonValue
from app.graph.models import digest,PathRecord

class Model(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True,frozen=True,hide_input_in_errors=True)


def text(value):
    if not isinstance(value,str):raise ValueError('Expected text, no coercion')
    value=unicodedata.normalize('NFKC',value).strip()
    if not value or any(ord(c)<32 and c not in '\n\r\t' for c in value):raise ValueError('Blank/control-character text')
    return value


def utc(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})',value):raise ValueError('Expected ISO timestamp with explicit timezone')
    return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc).isoformat(timespec='microseconds').replace('+00:00','Z')

ID=Annotated[str,Field(min_length=1,max_length=200),AfterValidator(text)]
UNITS={'water_depth':{'cm':('cm',1),'m':('cm',100),'mm':('cm',.1)},
       'duration':{'min':('min',1),'hours':('min',60)},'rainfall':{'mm':('mm',1),'cm':('mm',10)},
       'drain_capacity':{'m3/s':('m3/s',1)},'pothole_depth':{'cm':('cm',1),'mm':('cm',.1),'m':('cm',100)},
       'damage_area':{'m2':('m2',1),'cm2':('m2',.0001)},'waste_quantity':{'L':('L',1),'m3':('L',1000)}}

class Measurement(Model):
    name: Literal['water_depth','duration','rainfall','drain_capacity','pothole_depth','damage_area','waste_quantity']
    value: float=Field(ge=0,allow_inf_nan=False)
    unit: str=Field(min_length=1,max_length=20)
    observed_at: str
    source_id: ID
    source_reference: ID
    basis: Literal['OBSERVED','REPORTED','DERIVED']='REPORTED'
    evidence_id: ID|None=None
    _time=field_validator('observed_at')(utc)
    _source=field_validator('source_id','source_reference')(text)
    @model_validator(mode='after')
    def units(self):
        if self.unit not in UNITS[self.name]:raise ValueError('Unsupported measurement unit for quantity')
        if not math.isfinite(self.value*UNITS[self.name][self.unit][1]):raise ValueError('Canonical measurement overflow')
        return self
    def canonical(self):
        unit,factor=UNITS[self.name][self.unit]
        return {**self.model_dump(mode='json'),'value':float(Decimal(str(self.value))*Decimal(str(factor))),'unit':unit,'verification_status':'REPORTED','original_value':self.value,'original_unit':self.unit}

class Claim(Model):
    kind: ID
    statement: str=Field(min_length=1,max_length=1000)
    source_id: ID
    source_reference: ID
    _text=field_validator('kind','statement','source_id','source_reference')(text)

class Details(Model):
    measurements: list[Measurement]=Field(default_factory=list,max_length=10)
    claims: list[Claim]=Field(default_factory=list,max_length=10)

class WaterDetails(Details):
    rainfall_station_reference: ID|None=None
    rainfall_from: str|None=None
    rainfall_to: str|None=None
    _times=field_validator('rainfall_from','rainfall_to')(lambda v:utc(v) if v is not None else v)
    @model_validator(mode='after')
    def period(self):
        if self.rainfall_from and self.rainfall_to and self.rainfall_from>self.rainfall_to:raise ValueError('Rainfall interval reversed')
        return self
class RoadDetails(Details):
    distress_description: str|None=Field(default=None,max_length=1000)
class WasteDetails(Details):
    quantity_description: str|None=Field(default=None,max_length=1000)
    reported_pickup_status: Literal['MISSED','PARTIAL','COMPLETED','UNKNOWN']='UNKNOWN'
    illegal_dumping_claim: bool|None=None

class BaseIntake(Model):
    description: str=Field(min_length=1,max_length=4000)
    source_id: ID
    external_record_id: ID
    source_channel: ID
    source_version: ID='1'
    source_kind: Literal['SYNTHETIC','PUBLIC','MUNICIPAL','USER','AGENT']='SYNTHETIC'
    reported_at: str
    occurred_at: str
    ended_at: str|None=None
    location_id: ID
    asset_ids: list[ID]=Field(default_factory=list,max_length=3)
    evidence_ids: list[ID]=Field(default_factory=list,max_length=10)
    event_reference: ID|None=None
    subtype: ID='UNSPECIFIED'
    severity: Literal['LOW','MODERATE','HIGH','CRITICAL']='MODERATE'
    _times=field_validator('reported_at','occurred_at')(utc)
    _end=field_validator('ended_at')(lambda v:utc(v) if v is not None else v)
    _ids=field_validator('source_id','external_record_id','source_channel','source_version','location_id','subtype')(text)
    _event=field_validator('event_reference')(lambda v:text(v) if v is not None else v)
    @field_validator('description')
    @classmethod
    def description_text(cls,v):return ' '.join(text(v).split())
    @field_validator('asset_ids','evidence_ids')
    @classmethod
    def ids(cls,v):
        normalized=[text(x) for x in v]
        if len(set(normalized))!=len(normalized):raise ValueError('Duplicate references')
        return sorted(normalized)
    @model_validator(mode='after')
    def chronology(self):
        if self.occurred_at>self.reported_at or (self.ended_at and not self.occurred_at<=self.ended_at<=self.reported_at):raise ValueError('Occurrence/report interval inconsistent')
        for m in self.details.measurements:
            if m.observed_at>self.reported_at:raise ValueError('Measurement after report')
        if self.issue_type=='WATERLOGGING' and self.details.rainfall_to and self.details.rainfall_to>self.reported_at:raise ValueError('Rainfall observation interval after report')
        allowed={'WATERLOGGING':{'water_depth','duration','rainfall','drain_capacity'},'ROAD_DAMAGE':{'pothole_depth','damage_area'},'WASTE_ACCUMULATION':{'waste_quantity'}}[self.issue_type]
        if any(m.name not in allowed for m in self.details.measurements):raise ValueError('Measurement belongs to a different issue')
        return self
class WaterIntake(BaseIntake):
    issue_type: Literal['WATERLOGGING']
    details: WaterDetails=Field(default_factory=WaterDetails)
class RoadIntake(BaseIntake):
    issue_type: Literal['ROAD_DAMAGE']
    details: RoadDetails=Field(default_factory=RoadDetails)
class WasteIntake(BaseIntake):
    issue_type: Literal['WASTE_ACCUMULATION']
    details: WasteDetails=Field(default_factory=WasteDetails)
INTAKE=TypeAdapter(Annotated[WaterIntake|RoadIntake|WasteIntake,Field(discriminator='issue_type')])

class Normalized(Model):
    original: dict[str,JsonValue]
    canonical: dict[str,JsonValue]
    request_hash: str

def normalize(payload):
    if not isinstance(payload,dict):raise ValueError('Intake requires a JSON object')
    def json_only(v):
        if isinstance(v,dict):
            if not all(isinstance(k,str) for k in v):raise ValueError('JSON keys must be strings')
            for child in v.values():json_only(child)
        elif isinstance(v,list):
            for child in v:json_only(child)
        elif v is not None and type(v) not in (str,int,float,bool):raise ValueError('JSON values only; no implicit coercion')
    json_only(payload)
    raw=json.loads(json.dumps(payload,allow_nan=False))
    if len(json.dumps(raw).encode())>32768:raise ValueError('Intake exceeds32KiB')
    request=INTAKE.validate_python(raw);canonical=request.model_dump(mode='json')
    for encoded,m in zip(canonical['details']['measurements'],request.details.measurements,strict=True):
        converted=m.canonical();encoded['value']=converted['value'];encoded['unit']=converted['unit']
    return request,Normalized(original=raw,canonical=canonical,request_hash=digest(canonical))

class HistorySummary(Model):
    id: str
    kind: Literal['Inspection','WorkOrder','InterventionOutcome','PickupExecution']
    occurred_at: str|None=None
    status: str|None=None
    result: str|None=None

class Assessment(Model):
    measurements: list[dict[str,JsonValue]]=Field(default_factory=list,max_length=10)
    claims: list[Claim]=Field(default_factory=list,max_length=10)
    gaps: list[str]=Field(default_factory=list,max_length=100)
    contradictions: list[str]=Field(default_factory=list,max_length=100)
    history_ids: list[str]=Field(default_factory=list,max_length=100)
    history_records: list[HistorySummary]=Field(default_factory=list,max_length=100)
    source_evidence_ids: list[str]=Field(default_factory=list,max_length=100)

class EvidenceRef(Model):
    id: str
    recorded_at: str
    observed_at: str|None=None
    source_kind: str
    reliability: str

class IntakeResult(Model):
    graph: str
    municipality_id: Literal['demo-city']='demo-city'
    complaint_id: str
    incident_id: str
    cluster_id: str
    journal_id: str
    pattern_type: Literal['SINGLE_EVENT','PERSISTENT','RECURRENT','CROSS_CATEGORY']
    classification: Literal['SAME_INCIDENT','NEW_OCCURRENCE','CONTINUING_UNRESOLVED','AFTER_RECORDED_END','RELATED_CROSS_CATEGORY']
    created_incident: bool
    related_incident_ids: list[str]=Field(default_factory=list,max_length=100)
    matched_attributes: list[str]
    explanations: list[str]
    uncertainty: list[str]
    assessment: Assessment
    graph_paths: list[PathRecord]=Field(default_factory=list,max_length=100)
    source_evidence_ids: list[str]=Field(default_factory=list,max_length=100)
    evidence_references: list[EvidenceRef]=Field(default_factory=list,max_length=100)
    graph_revision: int
    as_of: str
    simulation_mode: Literal[True]=True
    search_limited: Literal[True]=True
    truncated: bool=False
    replayed: bool=False
    preview: bool=False
    historical_receipt: bool=False

class Journal(Model):
    version: Literal[1]=1
    operation: Literal['INTAKE','REGROUP']='INTAKE'
    state: Literal['PREPARED','COMMITTED']='PREPARED'
    original: dict[str,JsonValue]
    canonical: dict[str,JsonValue]
    request_hash: str
    receipt: dict[str,JsonValue]|None=None
    @model_validator(mode='after')
    def receipt_state(self):
        if (self.state=='COMMITTED')!=(self.receipt is not None):raise ValueError('Journal state/receipt inconsistent')
        return self
    def serialized(self):
        value=self.model_dump_json()
        if len(value.encode())>65536:raise ValueError('Journal exceeds64KiB')
        return value

class Review(Model):
    request_id: ID
    reviewer_id: ID
    role: Literal['ANALYST','ADMIN']
    reviewed: bool
    reason: str=Field(min_length=1,max_length=1000)
    incident_id: ID
    target_cluster_id: ID
    expected_incident_hash: str=Field(pattern='^[a-f0-9]{64}$')
    expected_membership_hash: str=Field(pattern='^[a-f0-9]{64}$')
    expected_target_hash: str=Field(pattern='^[a-f0-9]{64}$')
    _text=field_validator('request_id','reviewer_id','reason','incident_id','target_cluster_id')(text)
    @model_validator(mode='after')
    def accepted(self):
        if self.reviewed is not True:raise ValueError('Explicit review required')
        return self
