import pytest
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.modules.users.repository import UserRepository


@pytest.fixture(scope="session")
def postgres_temp_db():
    host = "127.0.0.1"
    user = "postgres"
    password = "postgres"
    port = 5432
    dbname = "test_ecommerce"

    with DatabaseJanitor(
        user=user, host=host, port=port, dbname=dbname, version=16, password=password
    ):
        yield f"postgresql+psycopg://{user}:{password}@{host}:{port}/{dbname}"


@pytest.fixture(scope="session")
def test_engine(postgres_temp_db):
    engine = create_engine(postgres_temp_db, echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(
        bind=test_engine, autoflush=True, autocommit=False, expire_on_commit=False
    )
    session = TestingSessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def user_repository(db_session):
    return UserRepository(db_session)
