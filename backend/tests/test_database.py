from app.database import normalize_url


def test_postgres_urls_use_the_psycopg_driver():
    # hosts hand out both spellings, and some add ssl options after the question mark
    for raw in ("postgres://user:pw@host/db", "postgresql://user:pw@host/db?sslmode=require"):
        url = normalize_url(raw)
        assert url.drivername == "postgresql+psycopg"
        assert url.host == "host"


def test_sqlite_urls_are_left_alone():
    assert normalize_url("sqlite:///./coach.db").drivername == "sqlite"