# Scope inventory

Includes host files inherited from the interrupted implementation and corrected here. Earlier accepted changes in these files are not attributed to this task. Frontend files excluded.

- `backend/app/demo_host/`
- `backend/app/events/service.py`
- `backend/app/events/worker.py`
- `backend/app/events/runtime.py`
- `backend/app/agents/runtime.py`
- `backend/app/agents/provider.py`
- `backend/app/agents/mcp.py`
- `backend/app/agents/prompts/DEMO-1.txt`
- `backend/app/services/planning/feedback.py`
- `backend/app/services/service_evidence.py`
- `backend/app/services/http/views.py`
- `backend/app/api/coverage.py`
- `backend/app/api/view_models.py`
- `backend/cli/main.py`
- `contracts/api_endpoints.json`
- `contracts/api_models.json`
- `contracts/operator_cli.json`
- `scripts/validate_api.py`
- `backend/tests/unit/test_demo_host.py`
- `backend/tests/integration/test_demo_host_runtime.py`
- `backend/DEMO_HOST.md`
- `backend/FRONTEND_HANDOFF.md`
- `backend/API.md`

Six tracking files receive append-only entries; new public evidence uses FRONTEND-BACKEND-DEMO-*; private runtime profiles, receipts and credentials live under .runtime/demo-presenter/run-01/. No secrets are included in public evidence.
