from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from agentic_workflow.utils.auth import User, get_current_user
from agentic_workflow.adk.models.workflow import WorkflowCore
from agentic_workflow.db.session import get_session
from agentic_workflow.db.models import WorkflowExecution
from agentic_workflow.crud.workflow import workflow as workflow_crud
from agentic_workflow.utils import helpers
from agentic_workflow.adk.models.workflow_execution import WorkflowExecutionCore
from agentic_workflow.crud.workflow_execution import workflow_execution as workflow_execution_crud
from agentic_workflow.workflow import workflow_orchestrator
from fastapi import HTTPException, Body
from typing import Dict, Any
from fastapi import Request
from agentic_workflow.workflow import temporal_client
from agentic_workflow.models.base import BaseResponse
from agentic_workflow.workflow.models.workflow_context import WorkflowContext
import logging


router = APIRouter(
    prefix="/v1/workflows/executions",
    tags=["workflows_executions"],
    responses={404: {"description": "Not found"}},
)

@router.post("/{workflow_id}/trigger", response_model=WorkflowExecution)
async def trigger_workflow_execution(
    *,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    workflow_id: str,
    body: Dict[str, Any] = Body(...),
    request: Request,
) -> WorkflowExecution:
    db_workflow = await workflow_crud.get(session=session, pk=workflow_id, user=user)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflowCore = WorkflowCore(**db_workflow.model_dump())

    stepInputPayload: Dict[str, Any] = {}
    stepInputPayload['headers'] = request.headers
    stepInputPayload['queryParams'] = request.query_params
    stepInputPayload['body'] = body
    
    temporalRunId = await workflow_orchestrator.init_workflow_orchestrator(workflow_id, workflowCore, stepInputPayload, user)

    if not temporalRunId:
        raise HTTPException(status_code=500, detail="Failed to trigger workflow")
    
    workflow_execution_core = WorkflowExecutionCore(
        workflowId=workflow_id,
        workflowRunId=temporalRunId,
        status=helpers.WorkflowStatus.RUNNING
    )
    db_workflow_execution = await workflow_execution_crud.create(session=session, obj_in=workflow_execution_core, user=user)

    return db_workflow_execution

@router.get("/{workflow_id}/run/{run_id}/history", response_model=WorkflowContext)
async def get_workflow_info(
    *, session: AsyncSession = Depends(get_session), workflow_id: str, run_id: str, user: User = Depends(get_current_user)
) -> WorkflowContext:
    workflow_execution = await workflow_execution_crud.get(session=session, pk=run_id, user=user)
    if not workflow_execution:
        raise HTTPException(status_code=404, detail="Workflow execution not found")
    
    temporalRunId = workflow_execution.workflowRunId
    workflow_run_history = await temporal_client.get_workflow_run_history(workflow_id, temporalRunId)
    workflow_context = WorkflowContext(**workflow_run_history)
    return workflow_context