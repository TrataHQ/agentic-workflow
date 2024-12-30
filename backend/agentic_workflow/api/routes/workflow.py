from fastapi import APIRouter, Depends
from agentic_workflow.workflow import workflow_orchestrator
from agentic_workflow.db.session import get_session
from agentic_workflow.utils.auth import get_current_user, User
from agentic_workflow.models.base import BaseResponse
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging
from agentic_workflow.adk.models.workflow import WorkflowCore
import jsonata

router = APIRouter(
    prefix="/v1/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)

@router.post("/{workflow_id}/trigger", response_model=BaseResponse)
async def trigger_workflow(
    *, session: AsyncSession = Depends(get_session), 
    user: User = Depends(get_current_user),
    workflow_id: str
):
    file_path = "test-dsl.json"
    with open(file_path, 'r') as file:
        data = json.load(file)

    workflowCore = WorkflowCore(**data)
    stepInputPayload = {}
    
    await workflow_orchestrator.init_workflow_orchestrator(workflow_id, workflowCore, stepInputPayload, user)

    return BaseResponse(message="Workflow triggered", status="success")

