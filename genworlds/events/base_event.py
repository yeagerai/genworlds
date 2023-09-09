from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BaseEvent(BaseModel):
    event_type: str
    description: str
    summary: Optional[str]
    created_at: datetime
    sender_id: str
    target_id: Optional[str] = Field(
        description="ID of the entity that handles the event"
    )