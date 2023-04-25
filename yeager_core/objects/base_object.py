from typing import List
from uuid import uuid4

from yeager_core.sockets.world_socket_client import WorldSocketClient
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.events.base_event import EventHandler, EventDict
from yeager_core.objects.base_object_events import GetObjectInfoEvent
from yeager_core.events.base_event import Listener


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

        self.important_event_types = important_event_types
        self.important_event_types.extend(["get_object_info"])

        self.event_dict = EventDict()
        self.event_dict.register_events([GetObjectInfoEvent])

        self.event_handler = EventHandler()
        self.event_handler.register_listener(
            event_type="get_object_info",
            listener=Listener(
                name="get_object_info",
                description="get_object_info",
                function=self.get_object_info,
            ),
        )

    async def get_object_info(self):
        event = GetObjectInfoEvent(
            object_name=self.name,
            object_id=self.id,
            object_description=self.description,
            possible_actions=self.important_event_types,
        )
        return event

    async def attach_to_world(self):
        with self.world_socket_client.ws_connection as websocket:
            while True:
                event = await websocket.recv()
                if event["event_type"] in self.important_event_types:
                    self.event_handler(event)
