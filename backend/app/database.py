from sqlalchemy import create_engine
from sqlalchemy.engine import URL, Engine, make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL


def normalize_url(url_text: str) -> URL:
    """Hosts hand out postgres:// or postgresql:// urls. The driver is named here
    so sqlalchemy uses psycopg 3, the one in requirements.txt."""
    url = make_url(url_text)
    if url.get_backend_name() in ("postgres", "postgresql"):
        return url.set(drivername="postgresql+psycopg")
    return url


def make_engine(url_text: str) -> Engine:
    url = normalize_url(url_text)

    if url.get_backend_name() == "sqlite":
        # sqlite refuses connections shared across threads by default, but fastapi
        # serves requests from a thread pool. only needed for sqlite
        return create_engine(url, connect_args={"check_same_thread": False})

    return create_engine(
        url,
        # a serverless instance needs only a couple of connections, the host pools the rest
        pool_size=2,
        max_overflow=0,
        pool_timeout=10,  # fail fast instead of hanging a request
        pool_pre_ping=True,  # replaces connections the database closed while idle
        # a pooled connection can't keep server-side prepared statements between requests
        connect_args={"prepare_threshold": None},
    )


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    # one session per request, closed when the request ends
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()