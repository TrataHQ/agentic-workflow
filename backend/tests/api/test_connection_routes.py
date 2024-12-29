from datetime import datetime, timedelta
import pytest
from agentic_workflow.adk.models.connection import ConnectionCore, OAuthCredentials
from tests.api.test_app_routes import create_test_app

async def test_create_connection(async_client, test_user):
    input, response = await create_test_connection(async_client)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == input.name
    assert data["orgId"] == test_user.tenantModel.orgId
    assert data["id"] is not None
    assert data["appId"] == input.appId
    assert data["credentials"] == input.credentials.model_dump(mode="json")

async def test_read_connections(async_client, test_user, db_session, auth_provider):
    # First create a test connection
    input, create_response = await create_test_connection(async_client)
    
    response = await async_client.get(
        "/v1/workflows/connections/",
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check if one of the connections is the one we created
    assert any(connection["id"] == create_response.json()["id"] for connection in data)
    assert any(connection["appId"] == input.appId for connection in data)
    assert any(connection["orgId"] == test_user.tenantModel.orgId for connection in data)

async def test_read_connection(async_client, test_user, db_session, auth_provider):
    # First create a test connection
    input, create_response = await create_test_connection(async_client)
    
    response = await async_client.get(
        f"/v1/workflows/connections/{create_response.json()['id']}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["orgId"] == test_user.tenantModel.orgId
    assert data["id"] == create_response.json()["id"]

async def test_update_connection(async_client, test_user, db_session, auth_provider):
    # Create test connection
    input, create_response = await create_test_connection(async_client)
    connection_id = create_response.json()["id"]
    
    update_data: ConnectionCore = ConnectionCore(
        name="Updated Connection Name",
        appId=input.appId,
        appVersion=input.appVersion,
        credentials=OAuthCredentials(
            code=None,
            accessToken="updated-access-token",
            refreshToken="updated-refresh-token",
            expiresAt=datetime.now()
        )
    )
    
    response = await async_client.put(
        f"/v1/workflows/connections/{connection_id}",
        json=update_data.model_dump(mode="json"),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data.name
    assert data["appId"] == update_data.appId
    assert data["credentials"] == update_data.credentials.model_dump(mode="json")
    assert data["orgId"] == test_user.tenantModel.orgId

async def test_delete_connection(async_client, test_user, db_session, auth_provider):
    # Create test connection
    input, create_response = await create_test_connection(async_client)
    connection_id = create_response.json()["id"]
    
    # Delete the connection
    response = await async_client.delete(
        f"/v1/workflows/connections/{connection_id}",
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Connection deleted successfully"
    
    # Verify connection is deleted
    get_response = await async_client.get(
        f"/v1/workflows/connections/{connection_id}",
    )
    assert get_response.status_code == 404

async def test_read_nonexistent_connection(async_client, test_user):
    response = await async_client.get(
        "/v1/workflows/connections/nonexistent-id",
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Connection not found"

async def create_test_connection(async_client):
    input, response = await create_test_app(async_client)
    appId = response.json()["app"]["id"]
    connection_data = ConnectionCore(
        name="Test Connection",
        appId=appId,
        appVersion=input.version,
        credentials=OAuthCredentials(
            code=None,
            accessToken="test-access-token",
            refreshToken="test-refresh-token",
            expiresAt=datetime.now() + timedelta(days=1)
        )
    )
    
    response = await async_client.post(
        "/v1/workflows/connections/",
        json=connection_data.model_dump(mode="json"),
    )
    return connection_data, response 