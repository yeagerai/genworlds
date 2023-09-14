from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BaseEvent(BaseModel):
    """
    Represents a foundational event in the simulation.

    BaseEvent serves as the parent class for various events that can occur in the 
    simulation. It defines core attributes that are intrinsic to all events, 
    including their type, description, creation timestamp, sender, and an optional target.

    Attributes:
        event_type (str): The type or category of the event.
        description (str): A detailed account of the event's purpose or significance.
        summary (Optional[str]): A brief overview of the event. Default is None.
        created_at (datetime): The time at which the event was created or initiated.
        sender_id (str): ID of the entity that emitted or initiated the event.
        target_id (Optional[str]): ID of the entity intended to handle or react to the event. Default is None.

    Args:
        event_type (str): The type or category of the event.
        description (str): A detailed account of the event's purpose or significance.
        summary (Optional[str]): A brief overview of the event.
        created_at (datetime): The time at which the event was created or initiated.
        sender_id (str): ID of the entity that emitted or initiated the event.
        target_id (Optional[str], optional): ID of the entity intended to handle or react to the event. Default is None.

    Example:
        my_event = BaseEvent(
            event_type="SampleEventType", 
            description="This event signifies ...",
            created_at=datetime.datetime.now(),
            sender_id="12345"
        )
    """
    event_type: str
    description: str
    summary: Optional[str]
    created_at: datetime
    sender_id: str
    target_id: Optional[str] = Field(
        description="ID of the entity that handles the event"
    )
