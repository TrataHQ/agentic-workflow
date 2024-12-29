from sqlmodel import SQLModel, Field
from typing import Dict, Any, TYPE_CHECKING
from agentic_workflow.adk.models.context import StepContext
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
from pydantic import BaseModel


# class WorkflowContext(SQLModel):
#     """Workflow Context Model"""
#     triggerPayload: Dict[str, Any] | None = Field(description="The payload of the trigger")
#     stepPayload: Dict[str, Any] | None = Field(description="The payload of the step")
#     stepResponse: Dict[str, Any] | None = Field(description="The response of the step")

# class WorkflowActionExecutionContext(SQLModel):
#     """Workflow Action Execution Context Model"""
#     # stepContext: StepContext = Field(description="The context of the step")
#     app: AppDefinition = Field(description="The app instance")
#     credentials: AppCredentials = Field(description="The credentials of the app")
#     data: Dict[str, Any] = Field(description="The data of the step")

class WorkflowActionExecutionContext(BaseModel):
    """Workflow Action Execution Context Model"""
    stepContext: StepContext = Field(description="The context of the step")
    app: AppDefinition = Field(description="The app instance")
    credentials: AppCredentials | None = Field(description="The credentials of the app") # TODO: Will update after implmented real app actions
    data: Dict[str, Any] = Field(description="The data of the step")

    class Config:
        arbitrary_types_allowed = True
