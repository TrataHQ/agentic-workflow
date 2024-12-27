from typing import Literal, Optional, Dict, List, Union, Type
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from src.db.utils import pydantic_column_type
from pydantic import BaseModel
from src.adk.models.connection import OAuthCredentials, ApiKeyCredentials, BasicAuthCredentials, NoAuthCredentials

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

class StepExecutorPayload(SQLModel):
    """Step Executor Payload Model"""
    executorType: Literal["http", "code"] = Field(description="The type of executor")

class Trigger(SQLModel):
    """Configuration for an App Trigger"""
    name: str = Field(description="The name of the step. This name should be unique within the app")
    description: Optional[str] = Field(default=None, description="The description of the step")
    dataSchema: Dict = Field(description="JSON Schema for the step data")
    uiSchema: Dict = Field(description="JSON Schema for the UI representation")

class Action(SQLModel):
    """Configuration for an App Action"""
    name: str = Field(description="The name of the step. This name should be unique within the app")
    description: Optional[str] = Field(default=None, description="The description of the step")
    dataSchema: Dict = Field(description="JSON Schema for the step data")
    uiSchema: Dict = Field(description="JSON Schema for the UI representation")


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
    triggers: List[Trigger] = Field(
        sa_column=Column(pydantic_column_type(List[Trigger])),
        description="Array of available triggers with their configurations"
    )
    actions: List[Action] = Field(
        sa_column=Column(pydantic_column_type(List[Action])),
        description="Array of available actions with their configurations"
    )
