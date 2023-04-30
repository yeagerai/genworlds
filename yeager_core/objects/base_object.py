from typing import List
from uuid import uuid4

from yeager_core.sockets.world_socket_client import WorldSocketClient
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.events.base_event import EventHandler, EventDict
from yeager_core.events.basic_events import AgentGetsObjectInfoEvent, ObjectSendsInfoToAgentEvent
from yeager_core.events.base_event import Listener


class BaseObject:
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
        self.id = uuid4()
        self.name = name
        self.description = description
        self.position = position
        self.size = size

        self.world_socket_client = WorldSocketClient()

        self.important_event_types = important_event_types
        self.important_event_types.extend(["agent_gets_object_info"])

        self.event_dict = event_dict
        self.event_dict.register_events([AgentGetsObjectInfoEvent])

        self.event_handler = event_handler
        self.event_handler.register_listener(
            event_type="agent_gets_object_info",
            listener=Listener(
                name="agent_gets_object_info_listener",
                description="Listens for an agent requesting object info.",
                function=self.agent_gets_object_info_listener,
            ),
        )

    async def agent_gets_object_info_listener(self, event: AgentGetsObjectInfoEvent):
        obj_info = ObjectSendsInfoToAgentEvent(
            agent_id=event.agent_id,
            object_id=self.id,
            object_name=self.name,
            object_description=self.description,
            possible_events=self.important_event_types,
        )
        await self.world_socket_client.send_message(obj_info.json())

    async def attach_to_world(self):
        with self.world_socket_client.ws_connection as websocket:
            while True:
                event = await websocket.recv()
                if (
                    event["event_type"] in self.important_event_types
                    and event["object_id"] == self.id
                ):
                    event_listener_name = self.event_handler.listeners[
                        event["event_type"]
                    ].name
                    parsed_event = self.event_dict.get_event_class(
                        event["event_type"]
                    ).parse_obj(event)
                    self.event_handler.handle_event(parsed_event, event_listener_name)
