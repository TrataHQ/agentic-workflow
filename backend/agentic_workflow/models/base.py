from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import event
from sqlalchemy.sql import text


class TimestampModel(SQLModel):
    createdBy: str = Field(
        default=None, nullable=False, description="The user who created."
    )
    createdAt: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
        description="The date and time it was created.",
    )
    updatedBy: str = Field(
        default=None, nullable=False, description="The user who last updated."
    )
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.utcnow(),
        nullable=False,
        description="The date and time when it was last updated.",
    )


# Add SQLAlchemy event listeners to automatically update timestamps
@event.listens_for(TimestampModel, "before_insert")
def set_created_at(mapper, connection, target):
    target.createdAt = datetime.utcnow()
    target.updatedAt = datetime.utcnow()


@event.listens_for(TimestampModel, "before_update")
def set_updated_at(mapper, connection, target):
    target.updatedAt = datetime.utcnow()


class BaseResponse(SQLModel):
    message: str = Field(
        default=None, nullable=False, description="The message of the response"
    )
    status: str = Field(
        default=None, nullable=False, description="The status of the response"
    )


class TenantModel(SQLModel):
    orgId: str = Field(
        default=None, nullable=False, description="The workspace of the entity."
    )


class IDModel(SQLModel):
    id: str = Field(
        default=None, nullable=False, description="The unique identifier of the entity"
    )
