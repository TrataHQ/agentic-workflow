from typing import Literal, Union
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from src.db.utils import pydantic_column_type
from datetime import datetime

class BaseCredentials(SQLModel):
    credentialsType: Literal["oauth", "apikey", "basic", "noauth"] = Field(description="The type of credentials")

class OAuthCredentials(BaseCredentials):
    credentialsType: Literal["oauth"] = Field(default="oauth", description="Credential type identifier")
    code: str | None = Field(description="The code for the OAuth app")
    accessToken: str | None = Field(description="The access token for the OAuth app")
    refreshToken: str | None = Field(description="The refresh token for the OAuth app")
    expiresAt: datetime | None = Field(description="The expiration date of the access token")

class ApiKeyCredentials(BaseCredentials):
    credentialsType: Literal["apikey"] = Field(default="apikey", description="Credential type identifier")
    apiKey: str = Field(description="The API key for the app")

class BasicAuthCredentials(BaseCredentials):
    credentialsType: Literal["basic"] = Field(default="basic", description="Credential type identifier")
    username: str = Field(description="The username for the app")
    password: str = Field(description="The password for the app")

class NoAuthCredentials(BaseCredentials):
    credentialsType: Literal["noauth"] = Field(default="noauth", description="Credential type identifier")

AppCredentials = Union[OAuthCredentials, ApiKeyCredentials, BasicAuthCredentials, NoAuthCredentials]

class ConnectionCore(SQLModel, table=False):
    """Core Connection Model"""
    name: str = Field(default=None, nullable=False, description="The name of the connection")
    appId: str = Field(default=None, nullable=False, description="The unique identifier of the app")
    appVersion: str = Field(default=None, nullable=False, description="The version of the app")
    description: str | None = Field(default=None, nullable=True, description="The description of the connection")
    credentials: AppCredentials = Field(
        sa_column=Column(pydantic_column_type(AppCredentials)), 
        description="OAuth or API key authentication configuration"
    )
