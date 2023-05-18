import threading
from uuid import uuid4
from typing import List
import time

from genworlds.objects.base_object import BaseObject
from genworlds.worlds.base_world import BaseWorld


class Simulation:
    def __init__(
        self,
        name: str,
        description: str,
        world: BaseWorld,
        objects: List[tuple[BaseObject, dict]],
        agents: List[tuple[BaseObject, dict]],
    ):

        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.world = world
        self.objects = objects
        self.agents = agents


    def launch(self):        
        # Register agents and objects with the world
        for (agent, world_properties) in self.agents:
            agent.world_spawned_id = self.world.id
            self.world.register_agent(agent, **world_properties)

        for (obj, world_properties) in self.objects:
            obj.world_spawned_id = self.world.id
            self.world.register_object(obj, **world_properties)

        # Launch the world
        self.world.launch_websocket_thread()

        time.sleep(1)

        for (agent, world_properties) in self.agents:
            # start the agent's threads
            threading.Thread(
                target=agent.listening_antenna.world_socket_client.websocket.run_forever,
                name=f"Agent {agent.ai_name} Listening Thread",
                daemon=True,
            ).start()
            threading.Thread(
                target=agent.world_socket_client.websocket.run_forever,
                name=f"Agent {agent.ai_name} Speaking Thread",
                daemon=True,
            ).start()
            threading.Thread(
                target=agent.think, 
                name=f"Agent {agent.ai_name} Thinking Thread",
                daemon=True,
            ).start()

        for (obj, world_properties) in self.objects:
            # start the object's threads
            obj.launch_websocket_thread()


        # Make the application terminate gracefully
        while True:
            try:
                time.sleep(100)
            except KeyboardInterrupt:
                break
