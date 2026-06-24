from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.core.settings import settings


engine = create_engine(
    settings.database_url,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    finally:
        db.close()