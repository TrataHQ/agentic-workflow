from typing import Literal, Dict, List, Union
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Enum as SQLAlchemyEnum
from src.db.utils import pydantic_column_type
from enum import Enum

class BaseAuth(SQLModel):
    """Base class for authentication configuration"""
    authType: str = Field(description="The type of authentication")

class OAuth(BaseAuth):
    """OAuth authentication configuration"""
    authType: Literal["oauth"] = Field(default="oauth", description="The type of authentication")
    clientId: str = Field(description="The client ID for the OAuth app")
    clientSecret: str = Field(description="The client secret for the OAuth app")
    redirectUri: str = Field(description="The redirect URI for the OAuth app")
    scopes: List[str] | None = Field(default=None, description="The scopes for the OAuth app")
    authUrl: str = Field(description="The authorization URL for the OAuth app")
    tokenUrl: str = Field(description="The token URL for the OAuth app")

class ApiKeyAuth(BaseAuth):
    """API key authentication configuration"""
    authType: Literal["apikey"] = Field(default="apikey", description="The type of authentication")

class BasicAuth(BaseAuth):
    """Basic authentication configuration"""
    authType: Literal["basic"] = Field(default="basic", description="The type of authentication")

class NoAuth(BaseAuth):
    """No authentication configuration"""
    authType: Literal["noauth"] = Field(default="noauth", description="The type of authentication")

AuthType = Union[OAuth, ApiKeyAuth, BasicAuth, NoAuth]

class AppActionType(str, Enum):
    """Enum for step types"""
    TRIGGER = "trigger"
    ACTION = "action"

class AppActionEntity(SQLModel):
    """App Action Model"""
    actionType: AppActionType = Field(
        sa_column=Column(SQLAlchemyEnum(AppActionType), nullable=False), 
        description="The type of the step, can be either trigger or action"
    )
    name: str = Field(default=None, description="The name of the step. This name should be unique within the app", nullable=False)
    description: str = Field(default=None, description="The description of the step", nullable=False)
    dataSchema: Dict = Field(description="JSON Schema for the step data", sa_column=Column(pydantic_column_type(Dict), nullable=False))
    uiSchema: Dict = Field(description="JSON Schema for the UI representation", sa_column=Column(pydantic_column_type(Dict), nullable=False))

class AppActionCore(AppActionEntity):
    """App Action Model"""
    appId: str = Field(description="The ID of the app that this action belongs to", nullable=False)
    appVersion: str = Field(description="The version of the app that this action belongs to", nullable=False)

class AppCore(SQLModel):
    """Core App Model"""
    name: str = Field(default=None, nullable=False, description="The name of the app")
    description: str | None = Field(default=None, nullable=True, description="The description of the app")
    endpointUrl: str | None = Field(default=None, nullable=True, description="API Endpoint URL for the app")
    logoUrl: str | None = Field(default=None, nullable=True, description="URL to the app's logo image")
    auth: List[AuthType] = Field(
        sa_column=Column(pydantic_column_type(List[AuthType])), 
        description="Authentication configuration for the app"
    )
    version: str = Field(default=None, nullable=False, description="The version of the app")

class AppEntity(AppCore):
    """App DTO Model filled by user"""
    actions: List[AppActionEntity] = Field(
        sa_column=Column(pydantic_column_type(List[AppActionEntity])),
        description="Array of available actions with their configurations"
    )
