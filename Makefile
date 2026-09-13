.PHONY: help start stop restart status ps logs backend frontend mcp-server test-skill test-skill-live seed-demo test migrate seed verify-db clean

PYTHON := ./backend/venv/bin/python
UVICORN := ./backend/venv/bin/uvicorn
PYTEST := ./backend/venv/bin/pytest
ALEMBIC := ./backend/venv/bin/alembic

help:
	@echo "AI Industry News Daily - Management Commands:"
	@echo "  make start           - Start background services (Postgres, etc.)"
	@echo "  make stop            - Stop all background services"
	@echo "  make restart         - Restart background services"
	@echo "  make status          - Check health of Postgres, SearXNG, Firecrawl, Backend, Frontend"
	@echo "  make ps              - View container status (docker compose ps)"
	@echo "  make logs            - Tail container logs"
	@echo "  make backend         - Run FastAPI backend development server on :8000"
	@echo "  make frontend        - Run Vite frontend development server on :5173"
	@echo "  make mcp-server      - Run the Editorial MCP Server over stdio"
	@echo "  make run-agents      - Run Google ADK multi-agent editorial workflow (curated demo)"
	@echo "  make run-agents-live - Run Google ADK multi-agent workflow with live SearXNG discovery"
	@echo "  make adk-eval        - Run ADK Golden Evaluation benchmark suite"
	@echo "  make test-skill      - Run simulated editorial pipeline (mock)"
	@echo "  make test-skill-live - Run simulated editorial skill with live SearXNG discovery"
	@echo "  make seed-demo       - Seed multi-day demo briefings, audit candidates, and feedback"
	@echo "  make migrate         - Apply database migrations (alembic upgrade head)"
	@echo "  make seed            - Seed database categories and configurations"
	@echo "  make verify-db       - Run database tables and indexes verification"
	@echo "  make test            - Run full test suite (backend & agents)"
	@echo "  make test-agents     - Run ADK agent and tool test suite"
	@echo "  make clean           - Clean up python cache files"

start:
	@echo "Starting services..."
	docker compose up -d
	@echo "Services started. Run 'make status' to verify."

stop:
	@echo "Stopping services..."
	docker compose down
	@echo "Services stopped."

restart: stop start

ps:
	docker compose ps

logs:
	docker compose logs -f

status:
	@echo "=========================================="
	@echo "  AI Industry News Daily - Service Status "
	@echo "=========================================="
	@echo -n "Postgres (127.0.0.1:5432): "
	@docker compose exec -T postgres pg_isready -U ainews -d ainews 2>/dev/null && echo "✓ Running" || echo "✗ DOWN"
	@echo -n "SearXNG (127.0.0.1:8080): "
	@curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/ | grep -q "200" && echo "✓ Running (HTTP 200)" || echo "✗ DOWN"
	@echo -n "Firecrawl (127.0.0.1:3002): "
	@curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3002/ | grep -q -E "200|404" && echo "✓ Running" || echo "✗ DOWN"
	@echo -n "Backend API (127.0.0.1:8000): "
	@curl -s http://127.0.0.1:8000/api/health 2>/dev/null | grep -q "healthy" && echo "✓ Running (Healthy)" || echo "✗ Not running on :8000 (run 'make backend')"
	@echo -n "Frontend UI (127.0.0.1:5173): "
	@curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5173/ 2>/dev/null | grep -q "200" && echo "✓ Running (HTTP 200)" || echo "✗ Not running on :5173 (run 'make frontend')"
	@echo "  make mcp-server      - Run the Editorial MCP Server over stdio"
	@echo "=========================================="

backend:
	PYTHONPATH=. $(UVICORN) backend.app.main:app --host 0.0.0.0 --port 8000 --reload

migrate:
	$(ALEMBIC) upgrade head

seed:
	PYTHONPATH=. $(PYTHON) scripts/seed_database.py

verify-db:
	PYTHONPATH=. $(PYTHON) scripts/verify_db.py

test:
	PYTHONPATH=. $(PYTEST) backend/tests agents/tests -v

test-agents:
	PYTHONPATH=. $(PYTEST) agents/tests -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf .coverage

frontend:
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

run-agents:
	PYTHONPATH=. $(PYTHON) agents/run_editorial_workflow.py

run-agents-live:
	PYTHONPATH=. $(PYTHON) agents/run_editorial_workflow.py --live

adk-eval:
	PYTHONPATH=. $(PYTHON) agents/tests/eval/eval_runner.py

test-skill:
	PYTHONPATH=. $(PYTHON) scripts/simulate_editorial_run.py

test-skill-live:
	PYTHONPATH=. $(PYTHON) scripts/simulate_editorial_run.py --live

seed-demo:
	PYTHONPATH=. $(PYTHON) scripts/seed_demo_edition.py

mcp-server:
	PYTHONPATH=. $(PYTHON) -m editorial_mcp.server
