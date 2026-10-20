import os

# set before the app is imported, so tests never touch the real database file
os.environ["DATABASE_URL"] = "sqlite://"

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import ChatMessage, FoodEntry


@pytest.fixture
def session_factory():
    # fresh in-memory database for every test, so tests can't affect each other
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False)


@pytest.fixture
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def add_entry(session_factory):
    # inserts a food row directly, since no endpoint creates food yet
    def _add(device_id="test-device-1", day=date(2026, 10, 18), name="banana", calories=105):
        with session_factory() as db:
            entry = FoodEntry(
                device_id=device_id,
                day=day,
                name=name,
                serving="1 serving",
                grams=100,
                calories=calories,
                confidence="high",
            )
            db.add(entry)
            db.commit()
            return entry.id

    return _add


@pytest.fixture
def add_message(session_factory):
    def _add(device_id="test-device-1", role="user", text="hi"):
        with session_factory() as db:
            db.add(ChatMessage(device_id=device_id, role=role, text=text))
            db.commit()

    return _add