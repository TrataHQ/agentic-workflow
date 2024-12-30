from sqlmodel import SQLModel, Field
from typing import Dict, Any, TYPE_CHECKING
from agentic_workflow.adk.models.context import StepContext
from agentic_workflow.adk.models.connection import AppCredentials
from agentic_workflow.adk.models.app_definition import AppDefinition
from pydantic import BaseModel
from sqlalchemy import Column
from agentic_workflow.db.utils import pydantic_column_type

class WorkflowContext(SQLModel):
    """Workflow Context Model"""
    workflowId: str = Field(description="The ID of the workflow")
    triggerPayload: Dict[str, Any] = Field(description="The payload of the trigger")
    stepInput: Dict[str, Any] = Field(description="The input of the step")
    stepResponse: Dict[str, Any] = Field(description="The response of the step")