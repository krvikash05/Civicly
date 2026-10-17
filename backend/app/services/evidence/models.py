"""B09 strict internal commands and durable evidence/assessment snapshots."""
from typing import Annotated, Literal
import json
from pydantic import BaseModel, ConfigDict, Field, AfterValidator, TypeAdapter, field_validator, model_validator, JsonValue
from app.graph.models import PathRecord
from app.graph.schema import timestamp


def nonblank(value):
    if not value.strip() or any(ord(c) < 32 for c in value):
        raise ValueError('Blank/control-character text')
    return value.strip()


ID = Annotated[str, Field(min_length=1, max_length=200), AfterValidator(nonblank)]
Text = Annotated[str, Field(min_length=1, max_length=2000), AfterValidator(nonblank)]
Time = Annotated[str, AfterValidator(lambda v: (timestamp(v), v)[1])]
Hash = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]


class Model(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True, hide_input_in_errors=True)


class Actor(Model):
    id: ID
    role: Literal['ANALYST', 'DEPARTMENT_LEAD', 'ADMIN', 'APPROVER']
    department_id: ID | None = None


class Review(Model):
    reviewer_id: ID
    role: Literal['ANALYST', 'ADMIN']
    reviewed: Literal[True]
    reason: Text

    @field_validator('reviewed', mode='before')
    @classmethod
    def boolean_only(cls, value):
        if type(value) is not bool:
            raise ValueError('Review requires explicit boolean')
        return value


class Topology(Model):
    source_id: ID
    target_id: ID
    operation: Literal['reachability', 'dependencies'] = 'reachability'
    max_hops: int = Field(default=4, ge=1, le=6)


class Command(Model):
    request_id: ID

    @field_validator('incident_ids', 'asset_ids', 'evidence_ids', 'confirming_codes', 'falsifying_codes', check_fields=False)
    @classmethod
    def distinct(cls, values):
        if len(set(values)) != len(values):
            raise ValueError('Duplicate references/codes')
        return sorted(values)


class OpenInvestigation(Command):
    operation: Literal['open'] = 'open'
    incident_ids: list[ID] = Field(min_length=1, max_length=3)
    cluster_id: ID
    priority: Literal['LOW', 'MODERATE', 'HIGH', 'CRITICAL'] = 'MODERATE'


class Propose(Command):
    operation: Literal['propose'] = 'propose'
    investigation_id: ID
    incident_ids: list[ID] = Field(min_length=1, max_length=3)
    asset_ids: list[ID] = Field(min_length=1, max_length=3)
    cause_code: ID
    statement: Text
    mechanism: Text
    confirming_codes: list[ID] = Field(min_length=1, max_length=10)
    falsifying_codes: list[ID] = Field(min_length=1, max_length=10)
    topology: Topology | None = None

    @model_validator(mode='after')
    def expectations(self):
        if set(self.confirming_codes) & set(self.falsifying_codes):
            raise ValueError('Confirming and falsifying codes must differ')
        if self.topology and self.topology.source_id == self.topology.target_id:
            raise ValueError('Topology requires distinct endpoints')
        return self


class RequestInspection(Command):
    operation: Literal['request_inspection'] = 'request_inspection'
    investigation_id: ID
    asset_ids: list[ID] = Field(min_length=1, max_length=3)
    department_id: ID
    inspection_type: ID


class TransitionInspection(Command):
    operation: Literal['transition_inspection'] = 'transition_inspection'
    inspection_id: ID
    expected_hash: Hash
    status: Literal['REQUESTED', 'SCHEDULED', 'IN_PROGRESS', 'FAILED', 'CANCELLED']
    scheduled_at: Time | None = None


class Observation(Model):
    asset_id: ID
    code: ID
    statement: Text
    method: ID
    observed_at: Time
    result: Literal['OBSERVED', 'UNKNOWN'] = 'OBSERVED'
    value: float | None = Field(default=None, allow_inf_nan=False)
    unit: ID | None = None

    @model_validator(mode='after')
    def quantity(self):
        if (self.value is None) != (self.unit is None):
            raise ValueError('Measured value and unit must be supplied together')
        return self


class ReportInspection(Command):
    operation: Literal['report_inspection'] = 'report_inspection'
    inspection_id: ID
    expected_hash: Hash
    source_id: ID
    record_id: ID
    source_kind: Literal['SYNTHETIC', 'MUNICIPAL', 'PUBLIC'] = 'SYNTHETIC'
    observations: list[Observation] = Field(min_length=1, max_length=10)
    review: Review | None = None


class Assess(Command):
    operation: Literal['assess'] = 'assess'
    hypothesis_id: ID
    expected_hash: Hash
    evidence_ids: list[ID] = Field(default_factory=list, max_length=20)
    as_of: Time


COMMAND = TypeAdapter(Annotated[OpenInvestigation | Propose | RequestInspection | TransitionInspection | ReportInspection | Assess, Field(discriminator='operation')])


class Report(Model):
    format_version: Literal[1] = 1
    inspection_id: ID
    inspector_id: ID
    department_id: ID
    source_id: ID
    record_id: ID
    source_kind: Literal['SYNTHETIC', 'MUNICIPAL', 'PUBLIC']
    observed_at: Time
    recorded_at: Time
    observations: list[Observation] = Field(min_length=1, max_length=10)
    finding_ids: list[ID] = Field(min_length=1, max_length=10)
    review: Review | None = None


class EvidenceReference(Model):
    id: ID
    content_hash: Hash
    source_kind: Literal['SYNTHETIC', 'PUBLIC', 'MUNICIPAL', 'USER', 'AGENT']
    source_record_id: str | None
    reliability: Literal['UNVERIFIED', 'CORROBORATED', 'VERIFIED']
    observed_at: Time | None
    recorded_at: Time
    basis: Literal['OBSERVED', 'REPORTED', 'DERIVED'] | None
    report: Report | None = None
    finding_hashes: dict[str, str] = Field(default_factory=dict)


class Assessment(Model):
    format_version: Literal[1] = 1
    id: ID
    hypothesis_id: ID
    previous_assessment_id: ID | None
    assessment: Literal['POSSIBLE', 'SUPPORTED', 'CONTRADICTED', 'VERIFIED', 'INCONCLUSIVE']
    rule_version: Literal[1] = 1
    cause_code: ID
    mechanism: Text
    confirming_codes: list[ID]
    falsifying_codes: list[ID]
    supporting_evidence_ids: list[ID]
    contradicting_evidence_ids: list[ID]
    evidence_references: list[EvidenceReference]
    excluded_evidence_ids: list[ID]
    missing_evidence: list[str]
    graph: str
    source_graph_revision: int
    graph_revision: int
    as_of: Time
    assessed_at: Time
    paths: list[PathRecord]
    path_ids: list[str]
    search_limited: Literal[True] = True
    truncated: bool
    state_transitions: list[str]
    reservations: list[str]


class Receipt(Model):
    operation: str
    journal_id: ID
    entity_id: ID
    graph: str
    graph_revision: int
    recorded_at: Time
    created_ids: list[ID]
    relationship_ids: list[ID]
    updated_ids: list[ID]
    assessment: Assessment | None = None
    replayed: bool = False
    historical_receipt: bool = True
    simulation_mode: Literal[True] = True


class InspectionView(Model):
    inspection_id: ID
    availability: Literal['AVAILABLE', 'UNAVAILABLE']
    state: str | None
    graph: str
    graph_revision: int
    as_of: Time
    requested_at: Time | None = None
    scheduled_at: Time | None = None
    completed_at: Time | None = None
    report_evidence_ids: list[ID] = Field(default_factory=list)
    finding_ids: list[ID] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class Journal(Model):
    format_version: Literal[1] = 1
    state: Literal['PREPARED', 'COMMITTED'] = 'PREPARED'
    request_hash: Hash
    actor: Actor
    command: dict[str, JsonValue]
    receipt: Receipt | None = None

    @model_validator(mode='after')
    def valid(self):
        COMMAND.validate_json(json.dumps(self.command))
        if (self.state == 'COMMITTED') != (self.receipt is not None):
            raise ValueError('Journal state/receipt mismatch')
        return self

    def serialized(self):
        raw = self.model_dump_json()
        if len(raw.encode()) > 131072:
            raise ValueError('B09 journal exceeds128KiB')
        return raw


def parse_command(payload):
    raw = json.dumps(payload, allow_nan=False)
    if len(raw.encode()) > 32768:
        raise ValueError('B09 request exceeds32KiB')
    return COMMAND.validate_json(raw)
