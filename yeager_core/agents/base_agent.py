from uuid import uuid4
from time import sleep
from typing import List

from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.objects.base_object import BaseObject
from yeager_core.sockets.world_socket_client import WorldSocketClient
from yeager_core.events.base_event import EventHandler, EventDict, Listener


class BaseAgent:
    def __init__(
        self,
        name: str,
        description: str,
        position: Coordinates,
        size: Size,
        event_dict: EventDict,
        event_handler: EventHandler,
        important_event_types: List[str],
    ):
        self.important_event_types = important_event_types
        important_event_types.extend(
            [
                "agent_gets_world_objects_in_radius",
                "agent_interacts_with_object",
                "agent_gets_object_info",
                "agent_move_to_position",
            ]
        )

        self.event_dict = event_dict

        self.id = uuid4()
        self.name = name
        self.description = description
        self.position = position
        self.size = size
        self.world_socket_client = WorldSocketClient()

    async def auto_pilot(self):
        # think + emit events
        # act + emit event
        # walk + emit event
        # default behavior
        while True:
            print("auto_pilot mode: on")
            sleep(10)

    async def attach_to_world(self):
        self.auto_pilot
        with self.world_socket_client.ws_connection as websocket:
            while True:
                event = await websocket.recv()
                if event["event_type"] in self.important_event_types:
                    self.event_handler(event)
