from typing import List
from uuid import uuid4

from yeager_core.worlds.world_socket_client import WorldSocketClient
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.events.base_event import EventHandler, EventDict


class BaseObject:
    def __init__(
        self,
        name: str,
        description: str,
        position: Coordinates,
        size: Size,
        important_event_types: List[str],
    ):
        self.id = uuid4()
        self.name = name
        self.description = description
        self.position = position
        self.size = size

        self.world_socket_client = WorldSocketClient()
        self.event_handler = EventHandler()
        self.event_dict = EventDict()
        self.important_event_types = important_event_types
        self.important_event_types.extend(["move_object_to_new_position", "get_object_info", "interact_with_object"])

    async def emit_event(self):
        while True:
            pass

    async def attach_to_world(self):
        with self.world_socket_client.ws_connection as websocket:
            while True:
                event = await websocket.recv()
                if event["event_type"] in self.important_event_types:
                    self.event_handler(event)
