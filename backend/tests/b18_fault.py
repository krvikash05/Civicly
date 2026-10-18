"""Test-only CLI child fault injection; no fault switch in operator interface."""
import sys
from app.services.evidence.service import EvidenceService
from cli.main import main
original=EvidenceService.readback

def mismatch(self,receipt):
 original(self,receipt)
 raise ValueError('Injected post-commit readback mismatch; private text must not escape')
EvidenceService.readback=mismatch
raise SystemExit(main(sys.argv[1:]))
