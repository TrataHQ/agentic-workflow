from agentic_workflow.adk.models.app import (
    AppActionEntity,
    AppActionType,
    AppCore,
    AppEntity,
    OAuth,
)
from agentic_workflow.main import create_app


async def test_status(test_user, async_client):
    """Test the status endpoint"""
    response = await async_client.get("/workflows/status")
    assert response.status_code == 200
    assert response.json() == {"status": "HEALTHY"}


async def test_create_app(async_client, test_user):
    input, response = await create_test_app(async_client)

    assert response.status_code == 200
    data = response.json()
    assert (
        data["app"]["name"] == input.name
        and data["app"]["description"] == input.description
    )
    assert data["app"]["orgId"] == test_user.tenantModel.orgId
    assert data["app"]["id"] is not None
    assert data["app"]["logoUrl"] == input.logoUrl
    assert data["app"]["auth"] == [auth.model_dump() for auth in input.auth]
    assert data["app"]["version"] == input.version

    # New validation for actions
    for input_action in input.actions:
        matching_action = next(
            (a for a in data["actions"] if a["name"] == input_action.name), None
        )
        assert matching_action is not None
        assert matching_action["actionType"] == input_action.actionType
        assert matching_action["dataSchema"] == input_action.dataSchema
        assert matching_action["uiSchema"] == input_action.uiSchema
        assert matching_action["description"] == input_action.description


async def test_read_apps(async_client, test_user, db_session, auth_provider):
    # First create a test app
    input, create_response = await create_test_app(async_client)

    response = await async_client.get(
        "/v1/workflows/apps/",
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check if one of the apps is the one we created
    assert any(app["app"]["id"] == create_response.json()["app"]["id"] for app in data)
    assert any(
        app["app"]["version"] == create_response.json()["app"]["version"]
        for app in data
    )
    assert any(app["app"]["orgId"] == test_user.tenantModel.orgId for app in data)


async def test_read_app(async_client, test_user, db_session, auth_provider):
    app = create_app(auth_provider)
    # First create a test app
    input, create_response = await create_test_app(async_client)

    response = await async_client.get(
        f"/v1/workflows/apps/{create_response.json()['app']['id']}",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["app"]["orgId"] == test_user.tenantModel.orgId
    assert data["app"]["id"] == create_response.json()["app"]["id"]


async def test_update_app(async_client, test_user, db_session, auth_provider):
    app = create_app(auth_provider)
    # Create test app
    input, create_response = await create_test_app(async_client)
    app_id = create_response.json()["app"]["id"]

    update_data = {
        "name": "Updated App Name",
        "description": "Updated Description",
        "logoUrl": "updated-icon",
        "auth": [
            {
                "type": "oauth",
                "clientId": "test-client-id",
                "clientSecret": "test-client-secret",
                "redirectUri": "http://localhost:8000/auth/callback",
            }
        ],
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
    assert data["app"]["name"] == update_data["name"]
    assert data["app"]["description"] == update_data["description"]
    assert data["app"]["orgId"] == test_user.tenantModel.orgId
    assert data["app"]["version"] == update_data["version"]


async def test_delete_app(async_client, test_user, db_session, auth_provider):
    app = create_app(auth_provider)
    # Create test app
    input, create_response = await create_test_app(async_client)
    app_id = create_response.json()["app"]["id"]

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


async def test_read_nonexistent_app(async_client, test_user, auth_provider):
    app = create_app(auth_provider)
    response = await async_client.get(
        "/v1/workflows/apps/nonexistent-id",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "App not found"


async def create_test_app(async_client):
    app_data: AppEntity = AppEntity(
        name="Test App",
        description="Test Description",
        logoUrl="test-icon",
        auth=[
            OAuth(
                authType="oauth",
                clientId="test-client-id",
                clientSecret="test-client-secret",
                redirectUri="http://localhost:8000/auth/callback",
                authUrl="https://example.com/auth",
                tokenUrl="https://example.com/token",
                scopes=["scope1", "scope2"],
            )
        ],
        version="1.0.0",
        actions=[
            AppActionEntity(
                name="Test Action",
                actionType=AppActionType.ACTION,
                dataSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"},
                    },
                    "required": ["name", "age"],
                },
                uiSchema={
                    "name": {"ui:widget": "text"},
                    "age": {"ui:widget": "number"},
                },
                description="Test Action Description",
            ),
            AppActionEntity(
                name="Test Trigger",
                actionType=AppActionType.TRIGGER,
                dataSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"},
                    },
                    "required": ["name", "age"],
                },
                uiSchema={
                    "name": {"ui:widget": "text"},
                    "age": {"ui:widget": "number"},
                },
                description="Test Trigger Description",
            ),
        ],
    )

    response = await async_client.post(
        "/v1/workflows/apps/",
        json=app_data.model_dump(),
    )
    return app_data, response
