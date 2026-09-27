import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.presentation.main import app
from app.infrastructure.database import Base, get_db

TEST_DB_URL="sqlite+aiosqlite:///:memory:"
engine_test=create_async_engine(TEST_DB_URL,connect_args={"check_same_thread":False})
TestingSessionLocal=async_sessionmaker(engine_test,class_=AsyncSession,expire_on_commit=False)

@pytest_asyncio.fixture
async def db_session():
    async with engine_test.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session: yield session
    async with engine_test.begin() as conn: await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db(): yield db_session
    app.dependency_overrides[get_db]=override_get_db
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://test") as ac: yield ac
    app.dependency_overrides.clear()
