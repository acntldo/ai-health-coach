import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models  # noqa: F401  (importing registers the tables)
from .config import GEMINI_API_KEY, GEMINI_MODELS, USDA_API_KEY
from .database import Base, engine
from .routers import chat, days, entries, messages

logger = logging.getLogger(__name__)

# local sqlite builds its tables when the app starts. a hosted database gets them from
# `python -m app.create_tables`, run once, so cold starts never touch the schema
if engine.url.get_backend_name() == "sqlite":
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # a chat without keys only fails once someone sends a message, so say it at startup
    settings = {"GEMINI_API_KEY": GEMINI_API_KEY, "GEMINI_MODELS": GEMINI_MODELS, "USDA_API_KEY": USDA_API_KEY}
    missing = [name for name, value in settings.items() if not value]
    if missing:
        logger.warning("missing settings: %s. the coach will answer 'unavailable' until they are set", ", ".join(missing))

    # uvicorn only prints the base url, so the useful links are printed here.
    # skipped on vercel and in docker, where localhost:8000 isn't how the app is reached
    if not os.getenv("VERCEL") and not os.getenv("IN_DOCKER"):
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

app.include_router(chat.router)
app.include_router(days.router)
app.include_router(entries.router)
app.include_router(messages.router)


@app.get("/api/health")
def health_check():
    # lets deploy checks and monitors confirm the api is up
    return {"status": "ok"}