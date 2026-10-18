"""Explicit public asset setup. No Gemini API, credentials or implicit runtime fetch."""
import hashlib,urllib.request
from app.agents.tokens import ASSET,SHA256,URL
if ASSET.exists():
    assert hashlib.sha256(ASSET.read_bytes()).hexdigest()==SHA256
else:
    data=urllib.request.urlopen(URL,timeout=60).read()
    assert hashlib.sha256(data).hexdigest()==SHA256
    ASSET.parent.mkdir(mode=0o700,parents=True,exist_ok=True);ASSET.write_bytes(data);ASSET.chmod(0o600)
print('PASS: pinned public tokenizer asset available offline; no Gemini request')
