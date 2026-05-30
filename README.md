# Graph Data Platform Demo

Production-style graph backend using **Python 3.12**, **FastAPI**, and **Neo4j**, designed for high-signal backend interviews.

## Key Features

- **Graph-native risk analytics**: `GET /api/v1/companies/{company_id}/risk` returns explainable paths and aggregate exposure score.
- **Safe bounded traversals**: only bounded path shapes are used (`TARGETS`, `WORKS_FOR`, `USES`, `OWNS`), with configurable `max_paths` limit.
- **Neo4j migrations**: idempotent startup migrations create and track UUID constraints/indexes via `(:Migration {id})` records.
- **Clean architecture + DI**: repository and service layers are injected through FastAPI dependencies (no global service locator).
- **FastAPI lifespan**: Neo4j driver lifecycle and migrations run during startup/shutdown.
- **Observability**: request-id based structured request logs and minimal counters for HTTP and graph-query usage.
- **Quality gates**: CI runs `ruff`, `mypy`, unit tests, and Neo4j-backed integration tests.

## API

- `GET /api/v1/health`
- `GET /api/v1/metrics`
- `POST /api/v1/companies`
- `GET /api/v1/companies/{company_id}`
- `GET /api/v1/companies/{company_id}/risk?max_paths=25`

## Local Run

```bash
docker compose up --build
```

Set env vars as needed:

- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- `NEO4J_DATABASE`
- `RISK_MAX_PATHS`

## Tests

```bash
ruff check .
mypy app
pytest -q tests/unit
RUN_INTEGRATION_TESTS=true pytest -q tests/integration
```
