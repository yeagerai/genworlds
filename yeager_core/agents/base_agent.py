from time import sleep
from typing import List

from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.objects.base_object import BaseObject


class BaseAgent(BaseObject):
    def __init__(
        self,
        name: str,
        description: str,
        position: Coordinates,
        size: Size,
        important_event_types: List[str],
    ):
        important_event_types.extend(["agent_move", "agent_think", "agent_act"])
        super().__init__(name, description, position, size, important_event_types)
        self.event_handler.register_listener()
        self.event_dict.register_events([])

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
