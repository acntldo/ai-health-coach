from . import models  # noqa: F401  (importing registers the tables)
from .database import Base, engine

# run once against a hosted database: python -m app.create_tables
# the url comes from the DATABASE_URL setting
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("tables ready")