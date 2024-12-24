from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class TimestampModel(SQLModel):
    createdBy: str = Field(default=None, nullable=False, description="The user who created.")
    createdAt: datetime = Field(default=None, nullable=False, description="The date and time it was created.")
    updatedBy: str = Field(default=None, nullable=False, description="The user who last updated.")
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        description="The date and time when it was last updated."
    )

class BaseResponse(SQLModel):
    message: str = Field(default=None, nullable=False, description="The message of the response")
    status: str = Field(default=None, nullable=False, description="The status of the response")

class TenantModel(SQLModel):
    orgId: str = Field(default=None, nullable=False, description="The workspace of the entity.")
