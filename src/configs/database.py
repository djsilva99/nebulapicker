from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.configs.settings import settings

# Engine & Session factory
engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
