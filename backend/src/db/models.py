# This file is used to define the models for the database

from datetime import datetime, timezone
from typing import Dict, List, ClassVar
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKeyConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import declared_attr
from src.db.utils import pydantic_column_type
from src.adk.models.app import AppCore
from src.adk.models.connection import ConnectionCore
from src.models.base import TimestampModel, TenantModel
from src.utils.helpers import generateRandomId, IdPrefix

#### Tables

class App(AppCore, TenantModel, TimestampModel, table=True):
    """App represents an integration that can be connected to perform actions and triggers"""

    __tablename__: ClassVar[str] = "workflows_app"
    id: str = Field(nullable=False, primary_key=True, description="The unique identifier of the app", default_factory=lambda: generateRandomId(IdPrefix.APP.value))

    __table_args__ = (
        PrimaryKeyConstraint('id', 'version', name='pk_app'),
    )

class Connection(ConnectionCore, TenantModel, TimestampModel, table=True):
    """Connection represents an instance of an app with specific credentials and configuration"""
    id: str = Field(nullable=False, primary_key=True, description="The unique identifier of the connection", default_factory=lambda: generateRandomId(IdPrefix.CONNECTION.value))

    __tablename__: ClassVar[str] = "workflows_connection"

    __table_args__ = (
        ForeignKeyConstraint(
            ['appId'], ['workflows_app.id'],
            name='fk_app_id',
            ondelete='CASCADE'
        ),
    )
