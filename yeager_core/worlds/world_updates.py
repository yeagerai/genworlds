from typing import Dict, Any
import random

from yeager_core.worlds.base_object import BaseObject
from yeager_core.worlds.base_world import BaseWorld
from yeager_core.agents.base_gen_agent import GenerativeAgent

def update_object_data(obj: BaseObject) -> Dict:
    # TODO: Implement the logic for updating the object data
    updated_data = obj.data  # Just a placeholder, replace with the actual updated data
    return updated_data

def update_agent_status(agent: GenerativeAgent, world: BaseWorld) -> str:
    # TODO: Implement the logic for updating the agent status
    new_status = "idle"  # Just a placeholder, replace with the actual updated status
    return new_status

def update_dynamic_world(world: BaseWorld) -> Dict[str, Any]:
    updates = {"object_updates": [], "agent_updates": []}

    # Update object positions and data based on world dynamics
    for obj in world.objects:
        # Update object position
        old_position = obj.position
        movement = [random.uniform(-1, 1) for _ in range(3)]  # Random movement in 3D space
        new_position = [coord + move for coord, move in zip(old_position, movement)]
        obj.position = new_position

        # Update object data
        new_data = update_object_data(obj)
        obj.data = new_data

        object_update = {
            "id": obj.id,
            "type": "object",
            "new_position": new_position,
            "new_data": new_data,
        }
        updates["object_updates"].append(object_update)

    # Update agent positions and status based on world dynamics
    for agent in world.agents:
        # Update agent position
        old_position = agent.position
        movement = [random.uniform(-1, 1) for _ in range(3)]  # Random movement in 3D space
        new_position = [coord + move for coord, move in zip(old_position, movement)]
        agent.position = new_position

        # Update agent status
        new_status = update_agent_status(agent, world)
        agent.status = new_status

        agent_update = {
            "id": agent.id,
            "type": "agent",
            "new_position": new_position,
            "new_status": new_status,
        }
        updates["agent_updates"].append(agent_update)

    return updates