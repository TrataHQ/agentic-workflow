from agentic_workflow.adk.models.workflow_execution import WorkflowExecutionCore
from agentic_workflow.db.models import WorkflowExecution
from sqlmodel.ext.asyncio.session import AsyncSession
from agentic_workflow.utils.auth import User
from agentic_workflow.crud.base import CRUDBase
from agentic_workflow.adk.models.workflow import WorkflowCore
from sqlmodel import select

class CRUDWorkflowExecution(CRUDBase[WorkflowExecution, WorkflowExecutionCore, WorkflowExecutionCore]):
    async def update_workflow_execution_status_by_temporal_run_id(self, session: AsyncSession, workflow_id: str, temporal_run_id: str, status: str, user: User) -> WorkflowExecution | None:
        statement = select(self.model).where(self.model.workflowId == workflow_id).where(self.model.workflowRunId == temporal_run_id).where(self.model.orgId == user.tenantModel.orgId)
        result = await session.exec(statement)
        workflow_execution = result.first()
        if workflow_execution:
            workflow_execution.status = status
            return await self.update(session=session, db_obj=workflow_execution, obj_in=workflow_execution, user=user)
        return None
    
workflow_execution = CRUDWorkflowExecution(WorkflowExecution, primary_keys=["id"])
