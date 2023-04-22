from typing import Dict, Callable, List
from pydantic import BaseModel

class Coordinates(BaseModel):
    x: float
    y: float
    z: float

class Size(BaseModel):
    width: float
    height: float
    depth: float

class BaseObject(BaseModel):
    id: str
    name: str
    description: str
    position: Coordinates
    size: Size
    event_queue: List[BaseModel]

    async def attach_to_world(self, websocket_manager):
        while True:
            # first check if the event contains the id of the blackboard
            # based on the event type, redirect if, and gather user or agent info
            # if the event coming from the socket is one of the events above, call the corresponding method
            pass
