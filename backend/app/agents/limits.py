"""Versioned Gemini Developer API capacity and independent host token profiles."""
from dataclasses import dataclass
from datetime import datetime,timezone

MODEL='gemini-3.8-flash'
INPUT_LIMIT=1_048_576
OUTPUT_LIMIT=65_536
MAX_RECEIPT_TOKENS=INPUT_LIMIT+OUTPUT_LIMIT
MAX_COUNT_RESPONSE=2**31-1
DEFAULT_CUMULATIVE_TOKENS=400_000
COMPLEX_CUMULATIVE_TOKENS=800_000
MAX_CUMULATIVE_TOKENS=2_000_000
MAX_CHECKPOINT_TOKENS=4_000_000
TOKEN_PROFILES={'standard':DEFAULT_CUMULATIVE_TOKENS,'complex':COMPLEX_CUMULATIVE_TOKENS}

@dataclass(frozen=True)
class CountBillingPolicy:
    """Only this exact published Google endpoint contract; no other endpoint implied."""
    version:str='google-developer-countTokens-nonbillable-2026-10-18'
    verified:bool=True
    valid_until:datetime=datetime(2027,1,1,tzinfo=timezone.utc)
    def nonbillable(self,model,now):
        return self.verified is True and self.version=='google-developer-countTokens-nonbillable-2026-10-18' and model==MODEL and datetime(2026,10,18,tzinfo=timezone.utc)<=now<self.valid_until
