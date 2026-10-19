from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

# sqlite refuses connections shared across threads by default, but fastapi
# serves requests from a thread pool. only needed for sqlite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
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