# This file is used to define the models for the database

from datetime import datetime, timezone
from typing import Dict, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKeyConstraint
from src.db.utils.utils import pydantic_column_type
from src.models.app import AppCore
from src.models.connection import ConnectionCore
from src.models.base import TimestampModel, TenantModel

#### Tables

class App(AppCore, TenantModel, TimestampModel, table=True):
    """App represents an integration that can be connected to perform actions and triggers"""

    __tablename__ = "workflows_app"
    id: str = Field(default=None, nullable=False, primary_key=True, description="The unique identifier of the app")

class Connection(ConnectionCore, TenantModel, TimestampModel, table=True):
    """Connection represents an instance of an app with specific credentials and configuration"""
    id: str = Field(default=None, nullable=False, primary_key=True, description="The unique identifier of the connection")

    __tablename__ = "workflows_connection"

    __table_args__ = (
        ForeignKeyConstraint(
            ['appId'], ['workflows_app.id'],
            name='fk_app_id',
            ondelete='CASCADE'
        ),
    )
