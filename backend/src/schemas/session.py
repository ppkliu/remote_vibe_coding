from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid
from ..models.session import SessionStatus

class SessionCreate(BaseModel):
    title: str | None = Field(None, max_length=255)
    working_directory: str = Field(default=".")

class SessionUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)

class SessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    ended_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
