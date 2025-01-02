from agentic_workflow.adk.models.workflow import (
    WorkflowCore,
    WorkflowStep,
    NextStepResolver,
    AppActionEntity,
)
from agentic_workflow.adk.models.app import AppActionType


async def test_create_workflow(async_client, test_user):
    input, response = await create_test_workflow(async_client)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == input.name
    assert data["description"] == input.description
    assert data["version"] == input.version
    assert data["startStepId"] == input.startStepId
    assert data["steps"] == input.model_dump()["steps"]


async def test_read_workflows(async_client, test_user, db_session):
    # First create a test workflow
    input, create_response = await create_test_workflow(async_client)

    response = await async_client.get("/v1/workflows/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(workflow["id"] == create_response.json()["id"] for workflow in data)
    assert any(workflow["name"] == input.name for workflow in data)


async def test_read_workflow(async_client, test_user, db_session):
    # First create a test workflow
    input, create_response = await create_test_workflow(async_client)
    workflow_id = create_response.json()["id"]

    response = await async_client.get(f"/v1/workflows/{workflow_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workflow_id
    assert data["name"] == input.name
    assert data["description"] == input.description


async def test_update_workflow(async_client, test_user, db_session):
    # Create test workflow
    input, create_response = await create_test_workflow(async_client)
    workflow_id = create_response.json()["id"]

    # Create update data using WorkflowCore model
    update_data = WorkflowCore(
        name="Updated Workflow Name",
        description="Updated Description",
        version="1.0.1",
        startStepId="step1",
        steps={
            "step1": WorkflowStep(
                stepId="step1",
                appConnectionId="conn1",
                appId="app1",
                appName="TestApp",
                appVersion="1.0.0",
                stepPayload=AppActionEntity(
                    name="Updated Action",
                    actionType=AppActionType.ACTION,
                    dataSchema={},
                    uiSchema={},
                    description="Updated action description",
                ),
                nextStepResolver=NextStepResolver(nextStepId="step1"),
            )
        },
    )

    response = await async_client.put(f"/v1/workflows/{workflow_id}", json=update_data.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data.name
    assert data["description"] == update_data.description
    assert data["version"] == update_data.version


async def test_delete_workflow(async_client, test_user, db_session):
    # Create test workflow
    input, create_response = await create_test_workflow(async_client)
    workflow_id = create_response.json()["id"]

    # Delete the workflow
    response = await async_client.delete(f"/v1/workflows/{workflow_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Workflow deleted successfully"

    # Verify workflow is deleted
    get_response = await async_client.get(f"/v1/workflows/{workflow_id}")
    assert get_response.status_code == 404


async def test_read_nonexistent_workflow(async_client, test_user):
    response = await async_client.get("/v1/workflows/nonexistent-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workflow not found"


async def create_test_workflow(async_client):
    workflow_data = WorkflowCore(
        name="Test Workflow",
        description="Test Description",
        version="1.0.0",
        startStepId="step1",
        steps={
            "step1": WorkflowStep(
                stepId="step1",
                appConnectionId="conn1",
                appId="app1",
                appName="TestApp",
                appVersion="1.0.0",
                stepPayload=AppActionEntity(
                    name="Test Action",
                    actionType=AppActionType.ACTION,
                    dataSchema={},
                    uiSchema={},
                    description="Test action description",
                ),
                nextStepResolver=NextStepResolver(nextStepId="step1"),
            )
        },
    )

    response = await async_client.post("/v1/workflows/", json=workflow_data.model_dump())
    return workflow_data, response
