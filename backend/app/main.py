import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  (importing registers the tables)
from .database import Base, engine

# fine at this size. a bigger app would use migrations instead
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # uvicorn only prints the base url, so the useful links are printed here.
    # skipped on vercel, where localhost links mean nothing
    if not os.getenv("VERCEL"):
        print("\n  Health check: http://127.0.0.1:8000/api/health")
        print("  API docs:     http://127.0.0.1:8000/api/docs\n")
    yield


# docs live under /api too, so everything the backend serves shares one prefix
app = FastAPI(
    title="AI Health Coach API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


@app.get("/api/health")
def health_check():
    # lets deploy checks and monitors confirm the api is up
    return {"status": "ok"}