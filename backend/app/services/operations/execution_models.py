"""B14 closed commands. Observations are data, never supplied outcome decisions."""
from typing import Annotated, Literal
from pydantic import Field
from app.services.evidence.models import (Model, ID, Hash, Text, Time, RequestInspection,
    TransitionInspection, ReportInspection, Assess)

class WorkCommand(Model):
    request_id: ID
    work_order_id: ID
    expected_hash: Hash

class Progress(WorkCommand):
    operation: Literal['progress'] = 'progress'
    action: Literal['START', 'BLOCK', 'FAIL', 'COMPLETE']
    reason: Text
    evidence_ids: list[ID] = Field(default_factory=list, max_length=10)

class Inspect(WorkCommand):
    operation: Literal['inspect'] = 'inspect'
    purpose: Literal['COMPLETION', 'FOLLOWUP', 'ASSESSMENT']
    command: Annotated[RequestInspection | TransitionInspection | ReportInspection | Assess,
                       Field(discriminator='operation')]
    review_reason: Text | None = None

class Evaluate(WorkCommand):
    operation: Literal['evaluate'] = 'evaluate'
    evidence_ids: list[ID] = Field(default_factory=list, max_length=10)
    window_start: Time
    window_end: Time

class Recur(Evaluate):
    operation: Literal['recur'] = 'recur'
    verified_outcome_id: ID
    # Closed B08 input is validated by its canonical normalizer before any write.
    complaint: dict

COMMANDS = {c.model_fields['operation'].default:c for c in [Progress, Inspect, Evaluate, Recur]}
