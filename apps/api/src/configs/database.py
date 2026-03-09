from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.configs.settings import settings

# Engine & Session factory
engine = create_engine(settings.DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
