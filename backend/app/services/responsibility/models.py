"""Closed synthetic inventory assertion and independently authenticated review."""
from typing import Literal
from pydantic import Field,field_validator,model_validator
from app.services.evidence.models import Model,ID,Time,Hash,Text
from app.graph.schema import timestamp
class ResponsibilitySubmission(Model):
 asset_id:ID
 department_id:ID
 source_id:ID
 source_record_id:ID
 source_version:int=Field(default=1,ge=1,le=100)
 source_kind:Literal['SYNTHETIC']='SYNTHETIC'
 observed_at:Time
 valid_from:Time
 valid_to:Time|None=None
 @field_validator('observed_at','valid_from','valid_to')
 @classmethod
 def canonical(cls,v):return timestamp(v).isoformat(timespec='microseconds').replace('+00:00','Z') if v is not None else None
 @model_validator(mode='after')
 def chronology(self):
  if timestamp(self.observed_at)>timestamp(self.valid_from) or self.valid_to and timestamp(self.valid_to)<=timestamp(self.valid_from):raise ValueError('RESPONSIBILITY_INTERVAL')
  return self
class ResponsibilityReview(Model):
 expected_hash:Hash
 reviewed:Literal[True]
 reason:Text
 @field_validator('reviewed',mode='before')
 @classmethod
 def explicit(cls,v):
  if type(v) is not bool:raise ValueError('EXPLICIT_REVIEW_REQUIRED')
  return v
class SubmissionRecord(Model):
 format_version:Literal[1]=1
 command:ResponsibilitySubmission
 submitted_by:ID
 submitted_at:Time
 command_hash:Hash
class ReviewRecord(Model):
 format_version:Literal[1]=1
 submission_id:ID
 submission_hash:Hash
 reviewed_by:ID
 reviewed_at:Time
 reviewed:Literal[True]=True
 reason:Text
class ResponsibilityDTO(Model):
 id:ID
 asset_id:ID
 department_id:ID
 source_id:ID
 source_record_id:ID
 source_version:int
 source_kind:Literal['SYNTHETIC']='SYNTHETIC'
 observed_at:Time
 valid_from:Time
 valid_to:Time|None
 submitted_by:ID
 reviewed_by:ID|None
 status:Literal['SUBMITTED','VERIFIED']
 applicability:Literal['UNREVIEWED','HISTORICAL','FUTURE','CURRENT']
 expected_hash:Hash
 source_evidence_id:ID
 review_evidence_id:ID|None
 relationship_id:ID|None
 event_id:ID
 as_of:Time
 simulation_mode:Literal[True]=True

Submission=ResponsibilitySubmission
Review=ResponsibilityReview
