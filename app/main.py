# Entry point for the FastAPI application.
# Sets up logging on startup, mounts the API router, and exposes a health check.

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.routes import router
from app.core.logging import setup_logging
from app.db.database import Base, engine


# Run setup tasks when the server starts (and teardown when it stops).
@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    yield


app = FastAPI(
    title="DatAds Performance API",
    description="Aggregated ad performance metrics from multiple platforms",
    version="1.0.0",
    lifespan=lifespan,
)

# Register all /api/* routes defined in routes.py.
app.include_router(router)


# Redirect bare root "/" to the auto-generated Swagger docs page.
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get(
    "/health",
    tags=["System"],
    summary="Service health check",
    description="Liveness check.",
)
def health():
    # Simple liveness probe — used by load balancers and container orchestrators.
    return {"status": "ok"}
