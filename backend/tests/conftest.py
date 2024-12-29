import pytest
import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from agentic_workflow.db.session import AsyncSessionLocal, get_session
from httpx import AsyncClient, ASGITransport
from agentic_workflow.utils.auth import User
from agentic_workflow.models.base import TenantModel
from agentic_workflow.main import create_app
from tests.no_auth_provider import NoAuthProvider
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture(scope="session")
def session_org_id():
    """Generate a unique org ID for the entire test session"""
    return f"test_tenant_{uuid4()}"

@pytest.fixture
def auth_provider(session_org_id):
    return NoAuthProvider(org_id=session_org_id)

@pytest.fixture
def app(auth_provider):
    """Create a FastAPI app instance with the configured auth provider"""
    return create_app(auth_provider)

@pytest.fixture
async def async_client(app):
    """Create an async client using the configured app"""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine(event_loop):
    """Create a test database engine"""
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",
        echo=False
    )
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    session = AsyncSession(
        db_engine,
        expire_on_commit=False,
    )
    async with session as s:
        async with s.begin():
            yield s

@pytest.fixture(scope="session")
async def initialize_db_session(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
async def test_user(session_org_id) -> User:
    mock_user = User(
        id="1",
        email="test@test.com",
        role="admin",
        tenantModel=TenantModel(orgId=session_org_id)
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
    