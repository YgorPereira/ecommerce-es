import pytest
import pytest_asyncio
from faker import Faker
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.base import Base
from src.modules.categories.repository import CategoryRepository
from src.modules.products.repository import ProductRepository
from src.modules.users.repository import UserRepository

fake = Faker("pt_BR")


@pytest.fixture(scope="session")
def postgres_temp_db():
    host = "127.0.0.1"
    user = "postgres"
    password = "postgres"
    port = 5432
    dbname = "test_ecommerce"

    with DatabaseJanitor(
        user=user,
        host=host,
        port=port,
        dbname=dbname,
        version=16,
        password=password,
    ):
        yield f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"


@pytest_asyncio.fixture(scope="function")
async def test_engine(postgres_temp_db):
    engine = create_async_engine(postgres_temp_db, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncSession:  # type: ignore
    async_session = async_sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def user_repository(db_session):
    return UserRepository(db_session)


@pytest.fixture(scope="function")
def category_repository(db_session):
    return CategoryRepository(db_session)


@pytest.fixture(scope="function")
def product_repository(db_session):
    return ProductRepository(db_session)


@pytest.fixture(scope="session")
def faker():
    return fake
