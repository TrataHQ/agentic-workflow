from sqlmodel import SQLModel, Field
from typing import Dict, List, Optional
from src.adk.models.app import Trigger, Action
from pydantic import field_validator

class Condition(SQLModel):
    """Condition Model for branching/looping logic"""
    when: str = Field(description="Condition expression to evaluate")
    stepId: str = Field(description="Next step ID if condition is true")

class NextStepResolver(SQLModel):
    """Defines how to determine the next step"""
    conditions: Optional[List[Condition]] = Field(default=None, description="Array of conditions to evaluate")
    nextStepId: Optional[str] = Field(default=None, description="Direct next step ID")

    @field_validator('conditions', 'nextStepId')
    def validate_mutually_exclusive(cls, v, values):
        if v is not None and values.get('conditions' if 'nextStepId' in values else 'nextStepId') is not None:
            raise ValueError('Cannot specify both conditions and nextStepId')
        if v is None and values.get('conditions' if 'nextStepId' in values else 'nextStepId') is None:
            raise ValueError('Must specify either conditions or nextStepId')
        return v

class WorkflowStep(SQLModel):
    """Flow Step Model"""
    stepId: str = Field(default=None, nullable=False, description="The id of the step")
    appConnectionId: str = Field(default=None, nullable=False, description="The connection id of the app")
    stepPayload: Trigger | Action = Field(default=None, nullable=False, description="The step to be performed")
    dataResolver: Dict = Field(default=None, nullable=False, description="The data resolver on how to resolve the data for the step")
    nextStepResolver: NextStepResolver = Field(description="Resolver for determining the next step")

class WorkflowCore(SQLModel):
    """Core Workflow Model"""
    name: str = Field(default=None, nullable=False, description="The name of the workflow")
    description: str | None = Field(default=None, nullable=True, description="The description of the workflow")
    steps: Dict[str, WorkflowStep] = Field(default=None, nullable=False, description="The steps of the workflow")
    startStepId: str = Field(default=None, nullable=False, description="The id of the start step")
