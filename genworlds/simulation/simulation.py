from __future__ import annotations

import threading
from uuid import uuid4
from typing import List
import time

from genworlds.objects.abstracts.object import AbstractObject
from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.worlds.abstracts.world import AbstractWorld


class Simulation:
    def __init__(
        self,
        name: str,
        description: str,
        world: AbstractWorld,
        objects: List[tuple[AbstractObject, dict]],
        agents: List[tuple[AbstractAgent, dict]],
        stop_event: threading.Event = None,
    ):
        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.world = world
        self.objects = objects
        self.agents = agents
        self.stop_event = stop_event

    def add_agent(self, agent: AbstractAgent, **world_properties):
        self.agents.append([agent, world_properties])
        self.agents[-1][0].world_spawned_id = self.world.id
        self.world.add_agent(self.agents[-1][0], **self.agents[-1][1])
        self.agents[-1][0].launch()

    def add_object(self, obj: AbstractObject, **world_properties):
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
            agent.launch()

        for obj, world_properties in self.objects:
            time.sleep(0.1)
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
