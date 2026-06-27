from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.core.settings import settings

engine = create_async_engine(
    settings.database_url,
    echo=True,
)

SessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise