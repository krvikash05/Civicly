# B12-R audit attempts

`backend/.venv/bin/python /tmp/b12r-audit.py` initially stopped on an audit assertion expecting858total graph nodes. A sanitized read showed859:858CivicEntity domain nodes plus the retained schema-migration bookkeeping node;1246relationships. Corrected the audit query to count CivicEntity nodes. No database write, reset or test rerun.

The immediately following `git apply --reverse --check docs/evidence/B12R-changes.patch` failed because the earlier audit had stopped before generating the patch. Rerun after successful audit generation; exact final result recorded separately. `git diff --check` passed. This was an audit assumption, not a lost/new municipal record.
