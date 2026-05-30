from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.company_router import router as company_router
from app.api.v1.health_router import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging, request_logging_middleware
from app.db.neo4j import Neo4jClient
from app.migrations.runner import apply_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = get_settings()
    neo4j_client = Neo4jClient(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password,
        database=settings.neo4j_database,
    )
    apply_migrations(neo4j_client)
    app.state.neo4j_client = neo4j_client
    yield
    neo4j_client.close()


app = FastAPI(title="Graph Data Platform Demo", lifespan=lifespan)
app.middleware("http")(request_logging_middleware)
app.include_router(health_router, prefix="/api/v1")
app.include_router(company_router, prefix="/api/v1")
