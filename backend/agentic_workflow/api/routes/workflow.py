from fastapi import APIRouter, Depends
from agentic_workflow.workflow import workflow_orchestrator
from agentic_workflow.db.session import get_session
from agentic_workflow.utils.auth import get_current_user, User
from agentic_workflow.models.base import BaseResponse
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

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
    asyncio.create_task(workflow_orchestrator.init_workflow_orchestrator_worker())
    await workflow_orchestrator.init_workflow_orchestrator(user.tenantModel.orgId, workflow_id)
    return BaseResponse(message="Hello World", status="success")

