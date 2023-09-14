from __future__ import annotations

from uuid import uuid4
from genworlds.simulation.sockets.handlers.event_handler import (
    SimulationSocketEventHandler,
)


class BaseObject(SimulationSocketEventHandler):
    """
    Represents a foundational object in the simulation.

    BaseObject serves as the parent class for various entities in the simulation, 
    providing essential attributes like a unique identifier, name, and description. 
    It also inherits from SimulationSocketEventHandler, enabling it to communicate 
    via websockets.

    Attributes:
        id (str): Unique identifier for the object.
        name (str): Name of the object.
        description (str): Description or details about the object.

    Args:
        name (str): Name of the object.
        description (str): Description or details about the object.
        id (str, optional): Unique identifier for the object. Defaults to a new UUID if not provided.
        websocket_url (str, optional): URL for the websocket communication. Defaults to "ws://127.0.0.1:7456/ws".

    Example:
        my_object = BaseObject("ObjectName", "A simple object description")
    """    
    def __init__(
        self,
        name: str,
        description: str,
        id: str = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        self.id = id if id else str(uuid4())
        self.name = name
        self.description = description

        super().__init__(
            id=self.id,
            websocket_url=websocket_url,
        )
