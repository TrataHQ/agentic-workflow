import pytest
import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.session import AsyncSessionLocal, get_session
from httpx import AsyncClient, ASGITransport
from src.utils.auth import User
from src.models.base import TenantModel
from src.main import create_app
from tests.no_auth_provider import NoAuthProvider
from sqlalchemy import delete

app = create_app(NoAuthProvider())

@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture(scope="session")
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture(scope="session")
async def initialize_db_session(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
async def test_user() -> User:
    mock_user = User(
        id="1",
        email="test@test.com",
        role="admin",
        tenantModel=TenantModel(orgId="tenant1")
    )
    return mock_user 

@pytest.fixture(autouse=True)
async def cleanup_apps(async_client, db_session):
    yield
    # List all apps
    response = await async_client.get("/v1/workflows/apps/")
    if response.status_code == 200:
        apps = response.json()
        # Delete each app
        for app in apps:
            response = await async_client.delete(f"/v1/workflows/apps/{app['id']}")
            assert response.status_code == 200
    