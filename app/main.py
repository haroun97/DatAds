# Entry point for the FastAPI application.
# Sets up logging on startup, mounts the API router, and exposes a health check.

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.routes import router
from app.core.config import get_settings
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

# Allow the presentation site and local dev servers to call the API from the browser.
_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
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
