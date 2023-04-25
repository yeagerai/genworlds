import json
import asyncio
from uuid import uuid4
from typing import List, Dict, Callable, Any

from pydantic import BaseModel

from yeager_core.agents.base_agent import BaseAgent
from yeager_core.objects.base_object import BaseObject
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.worlds.world_socket_client import WorldSocketClient


class BaseWorld(BaseObject):
    def __init__(
        self,
        name: str,
        description: str,
        position: Coordinates,
        size: Size,
        important_event_types: List[str],
        objects: List[BaseObject],
        agents: List[BaseAgent],
    ):
        important_event_types.extend(
            [
                "world_add_object",
                "world_remove_object",
                "world_add_agent",
                "world_remove_agent",
            ]
        )
        super().__init__(name, description, position, size, important_event_types)
        self.objects = objects
        self.agents = agents

    async def event_handler(self):
        with self.worldsocket_client.ws_connection as websocket:
            while True:
                event = await websocket.recv()
                # parse to BaseModel
                if event["type"].startswith("world"):
                    if event["type"] == "world_add_object":
                        self.add_object(event["object"])
                    elif event["type"] == "world_remove_object":
                        self.remove_object(event["object"])
                    elif event["type"] == "world_add_agent":
                        self.add_agent(event["agent"])
                    elif event["type"] == "world_remove_agent":
                        self.remove_agent(event["agent"])

    def add_object(self, obj: BaseObject):
        self.objects.append(obj)

    def remove_object(self, obj: BaseObject):
        self.objects.remove(obj)
        # send update to socket

    def add_agent(self, agent: BaseAgent):
        self.agents.append(agent)
        # send update to socket

    def remove_agent(self, agent: BaseAgent):
        self.agents.remove(agent)
        # send update to socket

    async def launch(self):
        self.event_handler()
        for agent in self.agents:
            agent.attach_to_world()
        for obj in self.objects:
            obj.attach_to_world()
