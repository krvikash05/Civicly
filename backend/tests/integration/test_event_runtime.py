"""Reuse one accepted B14 fixture; extend only the recurrence resume for B15."""
import pytest
from tests.integration.test_memory_graphrag import memory
pytestmark=pytest.mark.integration

def test_event_recurrence_actual_mcp_saver(db,tmp_path,memory,monkeypatch):
 from tests import b14r_runtime,b15_runtime
 from tests.integration.test_execution_runtime import test_actual_three_issue_completion_verification_and_water_recurrence
 monkeypatch.setenv('CIVICLY_B14R_CHECKPOINT_PROOF','1')
 monkeypatch.setenv('CIVICLY_OPERATIONS_EVIDENCE_PREFIX','B15')
 monkeypatch.setattr(b14r_runtime,'resume',b15_runtime.consume)
 test_actual_three_issue_completion_verification_and_water_recurrence(db,tmp_path,memory,'WATERLOGGING')
