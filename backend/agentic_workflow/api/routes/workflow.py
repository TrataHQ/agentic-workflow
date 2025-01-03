from fastapi import APIRouter, Depends
from agentic_workflow.workflow import workflow_orchestrator
from agentic_workflow.db.session import get_session
from agentic_workflow.utils.auth import get_current_user, User
from agentic_workflow.models.base import BaseResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from agentic_workflow.adk.models.workflow import WorkflowCore, WorkflowStep
from agentic_workflow.db.models import Workflow
from agentic_workflow.crud.workflow import workflow as workflow_crud
from typing import Dict, Any, List
import json
import logging
from fastapi import HTTPException, Body
from agentic_workflow.workflow import temporal_client
from agentic_workflow.utils import helpers
from agentic_workflow.adk.models.app import AppActionEntity
from agentic_workflow.adk.models.app import AppActionType
from agentic_workflow.workflow.models.workflow_context import WorkflowContext

router = APIRouter(
    prefix="/v1/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Workflow)
async def create_workflow(
    *,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    workflow_in: WorkflowCore,
):
    return await workflow_crud.create(session=session, obj_in=workflow_in, user=user)


@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(
    *,
    session: AsyncSession = Depends(get_session),
    workflow_id: str,
    workflow_in: WorkflowCore,
    user: User = Depends(get_current_user),
):
    db_workflow = await workflow_crud.get(session=session, pk=workflow_id, user=user)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return await workflow_crud.update(session=session, db_obj=db_workflow, obj_in=workflow_in, user=user)


@router.get("/", response_model=List[Workflow])
async def read_workflows(
    *,
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(get_current_user),
):
    return await workflow_crud.get_multi(session=session, skip=skip, limit=limit, user=user)


@router.get("/{workflow_id}", response_model=Workflow)
async def read_workflow(
    *,
    session: AsyncSession = Depends(get_session),
    workflow_id: str,
    user: User = Depends(get_current_user),
):
    workflow = await workflow_crud.get(session=session, pk=workflow_id, user=user)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.delete("/{workflow_id}", response_model=BaseResponse)
async def delete_workflow(
    *,
    session: AsyncSession = Depends(get_session),
    workflow_id: str,
    user: User = Depends(get_current_user),
):
    db_workflow = await workflow_crud.get(session=session, pk=workflow_id, user=user)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await workflow_crud.remove(session=session, pk=workflow_id, user=user)
    return BaseResponse(message="Workflow deleted successfully", status="success")

@router.post("/{workflow_id}/app/test", response_model=Dict[str, Any])
async def test_workflow(
    *,
    session: AsyncSession = Depends(get_session),
    workflow_id: str,
    user: User = Depends(get_current_user),
    workflowStep: WorkflowStep,
):
    db_workflow = await workflow_crud.get(session=session, pk=workflow_id, user=user)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflowContext = WorkflowContext(
        workflowId=workflow_id,
        orgId=user.tenantModel.orgId,
        stepInput={},
        stepResponse={},
        stepOrder=[],
    )

    app = await workflow_orchestrator.prepApp(workflowContext, workflowStep)
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    credentials = await workflow_orchestrator.prepCredentials(workflowContext, workflowStep, user)
    stepContext = await workflow_orchestrator.prepStepContext(workflowContext, workflowStep)

    stepPayload: AppActionEntity = workflowStep.stepPayload
    actionName: str = stepPayload.name

    result: Dict[str, Any] = {}
    actions = app.appActions

    action = next((a for a in actions if a.getAppActionEntity.name == actionName), None)
    if action:
        result = await action.run(stepContext, app, credentials, workflowContext.model_dump())

    return result
