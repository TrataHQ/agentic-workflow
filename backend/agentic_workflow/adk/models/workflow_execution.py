from sqlmodel import SQLModel, Field


class WorkflowExecutionCore(SQLModel):
    """Core Workflow Execution Model"""
    workflowId: str = Field(default=None, nullable=False, description="The id of the workflow")
    workflowRunId: str = Field(default=None, nullable=False, description="The id of the workflow run")
    status: str = Field(default=None, nullable=False, description="The status of the workflow execution")