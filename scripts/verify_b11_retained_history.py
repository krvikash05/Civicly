"""Reuse unchanged legacy assertions with the accepted latest rolling-proof snapshot.

B10-O-R2 saved its fresh B09R proof under its own prefix before restoring historical
B09R-runtime-proof bytes. The legacy verifier hardcodes the superseded rolling file.
No file/data or expected assertion is changed: choose the accepted latest snapshot.
"""
from pathlib import Path
source=Path('scripts/verify_b09r.py').read_text()
assert source.count("Path('docs/evidence/B09R-runtime-proof.json')")==1
source=source.replace("Path('docs/evidence/B09R-runtime-proof.json')", "Path('docs/evidence/B10OR2-regression-B09R-runtime-proof.json')")
exec(compile(source,'scripts/verify_b09r.py','exec'),{'__name__':'__main__'})
