# This file is used to define the models for the database

from typing import ClassVar
from sqlmodel import Field
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint
from agentic_workflow.adk.models.app import (
    AppActionCore,
    AppCore,
    AppEntity,
    AppActionEntity,
)
from agentic_workflow.adk.models.connection import ConnectionCore
from agentic_workflow.adk.models.workflow import WorkflowCore
from agentic_workflow.adk.models.workflow_execution import WorkflowExecutionCore
from agentic_workflow.models.base import TimestampModel, TenantModel
from agentic_workflow.utils.helpers import generateRandomId, IdPrefix

#### Tables


class App(AppCore, TenantModel, TimestampModel, table=True):
    """App represents an integration that can be connected to perform actions and triggers"""

    __tablename__: ClassVar[str] = "workflows_app"
    id: str = Field(
        nullable=False,
        description="The unique identifier of the app",
        default_factory=lambda: generateRandomId(IdPrefix.APP.value),
    )

    __table_args__ = (PrimaryKeyConstraint("id", "version", name="pk_app"),)


class AppAction(AppActionCore, TenantModel, TimestampModel, table=True):
    """AppAction represents an action that can be performed by an app"""

    id: str = Field(
        nullable=False,
        primary_key=True,
        description="The unique identifier of the app action",
        default_factory=lambda: generateRandomId(IdPrefix.APP_ACTION.value),
    )

    __tablename__: ClassVar[str] = "workflows_app_action"

    __table_args__ = (
        ForeignKeyConstraint(
            ["appId", "appVersion"],
            ["workflows_app.id", "workflows_app.version"],
            name="fk_app_id_version",
        ),
        UniqueConstraint("appId", "appVersion", "name", name="unique_app_id_version_name"),
    )


class Connection(ConnectionCore, TenantModel, TimestampModel, table=True):
    """Connection represents an instance of an app with specific credentials and configuration"""

    id: str = Field(
        nullable=False,
        primary_key=True,
        description="The unique identifier of the connection",
        default_factory=lambda: generateRandomId(IdPrefix.CONNECTION.value),
    )

    __tablename__: ClassVar[str] = "workflows_connection"

    __table_args__ = (
        ForeignKeyConstraint(
            ["appId", "appVersion"],
            ["workflows_app.id", "workflows_app.version"],
            name="fk_app_id_version",
        ),
    )


class Workflow(WorkflowCore, TenantModel, TimestampModel, table=True):
    """Workflow represents a sequence of steps that can be performed by an app"""

    id: str = Field(
        nullable=False,
        description="The unique identifier of the workflow",
        default_factory=lambda: generateRandomId(IdPrefix.WORKFLOW.value),
    )

    __tablename__: ClassVar[str] = "workflows_workflow"

    __table_args__ = (
        PrimaryKeyConstraint('id', 'version', name='pk_workflow'),
    )

class WorkflowExecution(WorkflowExecutionCore, TenantModel, TimestampModel, table=True):
    """WorkflowExecution represents a single execution of a workflow"""
    id: str = Field(nullable=False, primary_key=True, description="The unique identifier of the workflow execution", default_factory=lambda: generateRandomId(IdPrefix.WORKFLOW_EXECUTION.value))

    __tablename__: ClassVar[str] = "workflows_execution"

    __table_args__ = (
        UniqueConstraint('workflowId', 'workflowRunId', name='unique_workflow_id_workflow_run_id'),
    )
