from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    echo=settings.ENVIRONMENT == "development",  # Enable SQL logging in development
    pool_pre_ping=True,  # Check connection health before using
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

Base = declarative_base()


def get_db() -> Session:
    """
    Dependency function to get a database session.
    Use with FastAPI's Depends(get_db) for dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
