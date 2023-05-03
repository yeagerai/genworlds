import threading
from uuid import uuid4
from typing import List

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

        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.position = position
        self.size = size
        self.world_socket_client = WorldSocketClient(process_event=self.process_event)
        self.objects = objects
        self.agents = agents

    def agent_gets_world_objects_in_radius_listener(
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
        self.world_socket_client.send_message(obj_info.json())

    def process_event(self, event):
        if (
            event["event_type"] in self.important_event_types
            and event["world_id"] == self.id
        ):
            event_listener_name = self.event_handler.listeners[event["event_type"]].name
            parsed_event = self.event_dict.get_event_class(
                event["event_type"]
            ).parse_obj(event)
            self.event_handler.handle_event(parsed_event, event_listener_name)

    def launch(self):
        threading.Thread(
            target=self.world_socket_client.websocket.run_forever,
            name=f"World {self.name} Thread",
        ).start()

        for agent in self.agents:
            agent.world_spawned_id = self.id
            threading.Thread(
                target=agent.listening_antena.world_socket_client.websocket.run_forever,
                name=f"Agent {agent.ai_name} Listening Thread",
            ).start()
            threading.Thread(
                target=agent.world_socket_client.websocket.run_forever,
                name=f"Agent {agent.ai_name} Speaking Thread",
            ).start()
            threading.Thread(
                target=agent.think, name=f"Agent {agent.ai_name} Thinking Thread"
            ).start()

        for obj in self.objects:
            obj.world_spawned_id = self.id
            threading.Thread(
                target=obj.world_socket_client.websocket.run_forever,
                name=f"Object {obj.name} Thread",
            ).start()
