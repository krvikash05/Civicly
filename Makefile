PYTHON ?= python3.12
VENV := backend/.venv/bin

.PHONY: configure setup up health migrate schema-status test-unit test-graph test-repositories test-persistence test-spec down
configure:
	$(PYTHON) scripts/configure_local.py
setup:
	$(PYTHON) -m venv backend/.venv
	$(VENV)/python -m pip install uv==0.13.1
	UV_CACHE_DIR=.uv-cache $(VENV)/uv sync --project backend --frozen --python $(PYTHON)
up: configure
	docker compose up -d --wait --wait-timeout 120
health:
	$(VENV)/civicly health
migrate:
	$(VENV)/civicly migrate
schema-status:
	$(VENV)/civicly schema-status
test-unit:
	$(VENV)/python -m pytest backend/tests/unit -v
test-graph:
	$(VENV)/python -m pytest backend/tests/integration -v -m 'not persistence'
test-persistence:
	$(VENV)/python -m pytest backend/tests/integration -v -m persistence --run-persistence
test-spec:
	$(VENV)/python scripts/validate_blueprint.py
	$(VENV)/python scripts/validate_handoff.py
down:
	docker compose down

test-repositories:
	$(VENV)/python -m pytest backend/tests/unit/test_graph_access_models.py backend/tests/integration/test_graph_access.py -v

.PHONY: mcp-setup mcp-configure mcp-proof test-mcp
mcp-setup:
	npm ci --prefix backend/mcp_runtime --ignore-scripts --no-audit --no-fund
mcp-configure:
	PYTHONPATH=backend $(VENV)/python -m app.mcp configure
mcp-proof: mcp-configure
	PYTHONPATH=backend $(VENV)/python -m app.mcp proof --output docs/evidence/B06-runtime-proof.json
test-mcp:
	$(VENV)/python -m pytest backend/tests/unit/test_mcp_broker_policy.py backend/tests/integration/test_official_mcp.py -v -s
