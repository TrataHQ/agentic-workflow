import pytest
from httpx import AsyncClient
from src.db.models.models import App
from fastapi.testclient import TestClient
from src.models.app import AppCore
from src.main import create_app
from tests.no_auth_provider import NoAuthProvider

app = create_app(NoAuthProvider())

async  def test_status(test_user):
    """Test the status endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/workflows/status")
        assert response.status_code == 200
        assert response.json() == {'status': 'HEALTHY'}


async def test_create_app(async_client, test_user, initialize_db_session):
    input, response = await create_test_app(async_client)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == input.name and data["description"] == input.description
    assert data["orgId"] == test_user.tenantModel.orgId
    assert data["id"] is not None
    assert data["logoUrl"] == input.logoUrl
    assert data["auth"] == input.auth
    assert data["version"] == input.version
    assert data["triggers"] == input.triggers
    assert data["actions"] == input.actions

async def test_read_apps(async_client, test_user, db_session):
    # First create a test app
    input, create_response = await create_test_app(async_client)
    
    response = await async_client.get(
        "/v1/workflows/apps/",
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["orgId"] == test_user.tenantModel.orgId
    assert data[0]["id"] == create_response.json()["id"]

async def test_read_app(async_client, test_user, db_session):
    # First create a test app
    input, create_response = await create_test_app(async_client)
    
    response = await async_client.get(
        f"/v1/workflows/apps/{create_response.json()['id']}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["orgId"] == test_user.tenantModel.orgId
    assert data["id"] == create_response.json()["id"]

async def test_update_app(async_client, test_user, db_session):
    # Create test app
    input, create_response = await create_test_app(async_client)
    app_id = create_response.json()["id"]
    
    update_data = {
        "name": "Updated App Name",
        "description": "Updated Description",
        "logoUrl": "updated-icon",
        "auth": {
            "type": "oauth2",
            "clientId": "test-client-id",
            "clientSecret": "test-client-secret",
            "redirectUri": "http://localhost:8000/auth/callback"
        },
        "version": "1.0.1",
        "triggers": [],
        "actions": [],
    }
    
    response = await async_client.put(
        f"/v1/workflows/apps/{app_id}",
        json=update_data,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["orgId"] == test_user.tenantModel.orgId

async def test_delete_app(async_client, test_user, db_session):
    # Create test app
    input, create_response = await create_test_app(async_client)
    app_id = create_response.json()["id"]
    
    # Delete the app
    response = await async_client.delete(
        f"/v1/workflows/apps/{app_id}",
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "App deleted successfully"
    
    # Verify app is deleted
    get_response = await async_client.get(
        f"/v1/workflows/apps/{app_id}",
    )
    assert get_response.status_code == 404

async def test_read_nonexistent_app(async_client, test_user):
    response = await async_client.get(
        "/v1/workflows/apps/nonexistent-id",
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "App not found" 


async def create_test_app(async_client):
    app_data: AppCore = AppCore(
        name="Test App",
        description="Test Description",
        logoUrl="test-icon",
        auth={
            "type": "oauth2",
            "clientId": "test-client-id",
            "clientSecret": "test-client-secret",
            "redirectUri": "http://localhost:8000/auth/callback"
        },
        version="1.0.0",
        triggers=[],
        actions=[],
    )
    
    response = await async_client.post(
        "/v1/workflows/apps/",
        json=app_data.model_dump(),
    )
    return app_data, response

