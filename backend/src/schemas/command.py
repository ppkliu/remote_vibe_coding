from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid
from ..models.message import MessageRole, MessageContentType

class CommandRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=10000)

class CommandResponse(BaseModel):
    message_id: uuid.UUID
    status: str = "processing"

class MessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: MessageRole
    content: str
    content_type: MessageContentType
    message_metadata: dict | None = None
    timestamp: datetime
    sequence_number: int
    is_streamed: bool

    model_config = ConfigDict(from_attributes=True)
