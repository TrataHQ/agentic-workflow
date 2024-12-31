from sqlalchemy import Column
from sqlmodel import SQLModel, Field
from typing import Dict, List, Optional
from agentic_workflow.adk.models.app import AppActionEntity
from pydantic import field_validator
from agentic_workflow.db.utils import pydantic_column_type
from pydantic import model_validator

class Condition(SQLModel):
    """Condition Model for branching/looping logic"""
    when: str = Field(description="Condition expression to evaluate")
    stepId: str = Field(description="Next step ID if condition is true")

class NextStepResolver(SQLModel):
    """Defines how to determine the next step"""
    conditions: Optional[List[Condition]] = Field(default=None, description="Array of conditions to evaluate")
    nextStepId: Optional[str] = Field(default=None, description="Direct next step ID")

    @field_validator('conditions', 'nextStepId')
    @classmethod
    def validate_mutually_exclusive(cls, v, info):
        field_name = info.field_name
        other_field = 'nextStepId' if field_name == 'conditions' else 'conditions'
        data = info.data
        if v is not None and data.get(other_field) is not None:
            raise ValueError('Cannot specify both conditions and nextStepId')
        if field_name == 'nextStepId' and v is None and data.get('conditions') is None:
            raise ValueError('Must specify either conditions or nextStepId')
            
        return v
    
    
class WorkflowStep(SQLModel):
    """Flow Step Model"""
    stepId: str = Field(default=None, nullable=False, description="The id of the step")
    appConnectionId: str = Field(default=None, nullable=False, description="The connection id of the app")
    appId: str = Field(default=None, nullable=False, description="The id of the app")
    appName: str = Field(default=None, nullable=False, description="The name of the app. It must match the app name in AppDefinition implementation")
    appVersion: str = Field(default=None, nullable=False, description="The version of the app. It must match the app version in AppDefinition implementation")
    stepPayload: AppActionEntity = Field(default=None, nullable=False, description="The step to be performed")
    dataResolver: str | None = Field(default=None, nullable=False, description="The data resolver on how to resolve the data for the step")
    nextStepResolver: NextStepResolver = Field(description="Resolver for determining the next step")

class WorkflowCore(SQLModel):
    """Core Workflow Model"""
    name: str = Field(default=None, nullable=False, description="The name of the workflow")
    description: str | None = Field(default=None, nullable=True, description="The description of the workflow")
    version: str = Field(default=None, nullable=False, description="The version of the workflow")
    steps: Dict[str, WorkflowStep] = Field(description="The steps of the workflow", sa_column=Column(pydantic_column_type(Dict[str, WorkflowStep])))
    startStepId: str = Field(default=None, nullable=False, description="The id of the start step")

    @field_validator('steps')
    @classmethod
    def validate_step_id_exists_in_workflow_step(cls, v, info):
        for step_id, workflowStep in v.items():
            if step_id != workflowStep.stepId:
                raise ValueError(f"Step ID mismatch: key '{step_id}' does not match step's `stepId` ({workflowStep.stepId}).")
        
            if workflowStep.nextStepResolver:
                if workflowStep.nextStepResolver.nextStepId:
                    if workflowStep.nextStepResolver.nextStepId not in v:
                        raise ValueError(f"Next step ID '{workflowStep.nextStepResolver.nextStepId}' does not exist in the workflow steps.")
                    
                if workflowStep.nextStepResolver.conditions:
                    for condition in workflowStep.nextStepResolver.conditions:
                        if condition.stepId and condition.stepId not in v:
                            raise ValueError(f"Condition step ID '{condition.stepId}' does not exist in the workflow steps.")   
                                
        return v

    @field_validator('startStepId')
    @classmethod
    def validate_start_step_id_exists_in_workflow_step(cls, v, info):
        steps = info.data.get("steps", {})
        if v not in steps:
            raise ValueError(f"Start step ID '{v}' does not exist in the workflow steps.")
        return v
    