from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.routes import router
from app.core.logging import setup_logging
from app.db.database import Base, engine


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

app.include_router(router)


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
    return {"status": "ok"}
