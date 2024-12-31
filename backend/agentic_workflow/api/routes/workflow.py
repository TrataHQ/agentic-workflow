from fastapi import APIRouter, Depends
from agentic_workflow.workflow import workflow_orchestrator
from agentic_workflow.db.session import get_session
from agentic_workflow.utils.auth import get_current_user, User
from agentic_workflow.models.base import BaseResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from agentic_workflow.adk.models.workflow import WorkflowCore
from agentic_workflow.db.models import Workflow
from agentic_workflow.crud.workflow import workflow as workflow_crud
from typing import Dict, Any, List
import json
from fastapi import HTTPException

router = APIRouter(
    prefix="/v1/workflows",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Workflow)
async def create_workflow(
    *, session: AsyncSession = Depends(get_session), 
    user: User = Depends(get_current_user),
    workflow_in: WorkflowCore
):
    return await workflow_crud.create(session=session, obj_in=workflow_in, user=user)

@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(
    *, session: AsyncSession = Depends(get_session), workflow_id: str, workflow_in: WorkflowCore, user: User = Depends(get_current_user)
):
    db_workflow = await workflow_crud.get(session=session, pk=workflow_id, user=user)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return await workflow_crud.update(session=session, db_obj=db_workflow, obj_in=workflow_in, user=user)

@router.get("/", response_model=List[Workflow])
async def read_workflows(
    *, session: AsyncSession = Depends(get_session), 
    skip: int = 0, 
    limit: int = 100, 
    user: User = Depends(get_current_user)
):
    return await workflow_crud.get_multi(session=session, skip=skip, limit=limit, user=user)

@router.get("/{workflow_id}", response_model=Workflow)
async def read_workflow(*, session: AsyncSession = Depends(get_session), workflow_id: str, user: User = Depends(get_current_user)):
    workflow = await workflow_crud.get(session=session, pk=workflow_id, user=user)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.delete("/{workflow_id}", response_model=BaseResponse)
async def delete_workflow(
    *, session: AsyncSession = Depends(get_session), workflow_id: str, user: User = Depends(get_current_user)
):
    db_workflow = await workflow_crud.get(session=session, pk=workflow_id, user=user)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await workflow_crud.remove(session=session, pk=workflow_id, user=user)
    return BaseResponse(message="Workflow deleted successfully", status="success")


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
    stepInputPayload: Dict[str, Any] = {}
    
    await workflow_orchestrator.init_workflow_orchestrator(workflow_id, workflowCore, stepInputPayload, user)

    return BaseResponse(message="Workflow triggered", status="success")

