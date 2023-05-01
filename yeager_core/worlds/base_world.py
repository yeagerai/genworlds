from uuid import uuid4
from typing import List
import asyncio

from yeager_core.agents.yeager_autogpt.agent import YeagerAutoGPT
from yeager_core.objects.base_object import BaseObject
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.sockets.world_socket_client import WorldSocketClient
from yeager_core.events.base_event import EventHandler, EventDict, Listener
from yeager_core.events.basic_events import (
    AgentGetsWorldObjectsInRadiusEvent,
    WorldSendsObjectsInRadiusEvent,
)


class BaseWorld:
    def __init__(
        self,
        name: str,
        description: str,
        position: Coordinates,
        size: Size,
        event_dict: EventDict,
        event_handler: EventHandler,
        important_event_types: List[str],
        objects: List[BaseObject],
        agents: List[YeagerAutoGPT],
    ):
        self.important_event_types = important_event_types
        self.important_event_types.extend(
            [
                "agent_gets_world_objects_in_radius",
            ]
        )
        self.event_dict = event_dict
        self.event_dict.register_events([AgentGetsWorldObjectsInRadiusEvent])

        self.event_handler = event_handler
        self.event_handler.register_listener(
            event_type="agent_gets_world_objects_in_radius",
            listener=Listener(
                name="agent_gets_world_objects_in_radius_listener",
                description="Listens for an agent requesting objects in radius.",
                function=self.agent_gets_world_objects_in_radius_listener,
            ),
        )

        self.id = uuid4()
        self.name = name
        self.description = description
        self.position = position
        self.size = size
        self.world_socket_client = WorldSocketClient()
        self.objects = objects
        self.agents = agents

    async def agent_gets_world_objects_in_radius_listener(
        self, event: AgentGetsWorldObjectsInRadiusEvent
    ):
        objects_in_radius = []
        for obj in self.objects:
            if obj.position.distance_to(event.current_agent_position) <= event.radius:
                objects_in_radius.append(obj.id)
        obj_info = WorldSendsObjectsInRadiusEvent(
            agent_id=event.agent_id,
            world_id=self.id,
            object_ids_in_radius=objects_in_radius,
        )
        await self.world_socket_client.send_message(obj_info.json())

    async def attach_to_socket(self):
        while True:
            with self.world_socket_client.ws_connection as websocket:
                event = await websocket.recv()
                if (
                    event["event_type"] in self.important_event_types
                    and event["world_id"] == self.id
                ):
                    event_listener_name = self.event_handler.listeners[
                        event["event_type"]
                    ].name
                    parsed_event = self.event_dict.get_event_class(
                        event["event_type"]
                    ).parse_obj(event)
                    self.event_handler.handle_event(parsed_event, event_listener_name)

    def launch(self):
        asyncio.run(self.launch_async())

    async def launch_async(self):
        tasks = [
            self.attach_to_socket(),
            *[
                asyncio.create_task(agent.listening_antena.listen()) for agent in self.agents
            ],
            *[
                asyncio.create_task(agent.think()) for agent in self.agents
            ],
            *[
                asyncio.create_task(obj.attach_to_world()) for obj in self.objects
            ],
        ]
        await asyncio.gather(*tasks)
