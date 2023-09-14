from __future__ import annotations

import threading
from uuid import uuid4
from typing import List
import time

from genworlds.objects.base_object.base_object import BaseObject
from genworlds.agents.base_agent.base_agent import BaseAgent
from genworlds.worlds.base_world.base_world import BaseWorld


class Simulation:
    def __init__(
        self,
        name: str,
        description: str,
        world: BaseWorld,
        objects: List[tuple[BaseObject, dict]],
        agents: List[tuple[BaseObject, dict]],
        stop_event: threading.Event = None,
    ):
        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.world = world
        self.objects = objects
        self.agents = agents
        self.stop_event = stop_event

    def add_agent(self, agent: BaseAgent, **world_properties):
        self.agents.append([agent, world_properties])
        self.agents[-1][0].world_spawned_id = self.world.id
        self.world.add_agent(self.agents[-1][0], **self.agents[-1][1])
        self.agents[-1][0].launch_threads()

    def add_object(self, obj: BaseObject, **world_properties):
        self.objects.append([obj, world_properties])
        self.objects[-1][0].world_spawned_id = self.world.id
        self.world.add_object(self.objects[-1][0], **self.objects[-1][1])
        self.objects[-1][0].launch_websocket_thread()

    # TODO: delete objects and agents
    # TODO: update and restart objects and agents

    def launch(self):
        # Register agents and objects with the world
        for agent, world_properties in self.agents:
            agent.world_spawned_id = self.world.id
            self.world.register_agent(agent, **world_properties)

        for obj, world_properties in self.objects:
            obj.world_spawned_id = self.world.id
            self.world.register_object(obj, **world_properties)

        # Launch the world
        self.world.launch_websocket_thread()

        time.sleep(1)

        for agent, world_properties in self.agents:
            time.sleep(0.1)
            # start the agent's threads
            agent.launch_threads()

        for obj, world_properties in self.objects:
            time.sleep(0.1)
            # start the object's threads
            obj.launch_websocket_thread()

        # Make the application terminate gracefully
        while True:
            # TODO: pass the stop event to the world and the objects and the agents
            if self.stop_event and self.stop_event.is_set():
                break

            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
