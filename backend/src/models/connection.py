

from typing import Dict
from sqlalchemy import Column
from sqlmodel import Field, SQLModel
from src.db.utils.utils import pydantic_column_type


class ConnectionCore(SQLModel, table=False):
    """Core Connection Model"""
    name: str = Field(default=None, nullable=False, description="The name of the connection")
    appId: str = Field(default=None, nullable=False, description="The unique identifier of the app")
    description: str | None = Field(default=None, nullable=True, description="The description of the connection")
    logoUrl: str | None = Field(default=None, nullable=True, description="URL to the connection's logo image")
    credentials: Dict = Field(
        sa_column=Column(pydantic_column_type(Dict)), 
        description="OAuth or API key authentication configuration"
    )
