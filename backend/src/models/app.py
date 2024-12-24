from typing import Optional, Dict, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from src.db.utils.utils import pydantic_column_type


class Trigger(SQLModel, table=False):
    """Configuration for an App Trigger"""
    name: str = Field(description="The name of the trigger")
    description: Optional[str] = Field(default=None, description="The description of the trigger")
    dataSchema: Dict = Field(description="JSON Schema for the trigger data")
    uiSchema: Dict = Field(description="JSON Schema for the UI representation")

class Action(SQLModel, table=False):
    """Configuration for an App Action"""
    name: str = Field(description="The name of the action")
    description: Optional[str] = Field(default=None, description="The description of the action")
    dataSchema: Dict = Field(description="JSON Schema for the action data")
    uiSchema: Dict = Field(description="JSON Schema for the UI representation")

class AppCore(SQLModel, table=False):
    """Core App Model"""
    name: str = Field(default=None, nullable=False, description="The name of the app")
    description: str | None = Field(default=None, nullable=True, description="The description of the app")
    logoUrl: str | None = Field(default=None, nullable=True, description="URL to the app's logo image")
    auth: Dict = Field(
        sa_column=Column(pydantic_column_type(Dict)), 
        description="OAuth or API key authentication configuration"
    )
    version: str = Field(default=None, nullable=False, description="The version of the app")
    triggers: List[Trigger] = Field(
        sa_column=Column(pydantic_column_type(List[Trigger])),
        description="Array of available triggers with their configurations"
    )
    actions: List[Action] = Field(
        sa_column=Column(pydantic_column_type(List[Action])),
        description="Array of available actions with their configurations"
    )
