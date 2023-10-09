from abc import ABC

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AbstractEvent(ABC, BaseModel):
    event_type: str
    description: str
    summary: Optional[str]
    created_at: datetime = Field(default_factory=datetime.now)
    sender_id: str
    target_id: Optional[str]
