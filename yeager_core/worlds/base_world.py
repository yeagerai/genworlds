from typing import List, Dict, Callable, Any
from pydantic import BaseModel
from yeager_core.agents.base_gen_agent import GenerativeAgent
import asyncio

class BaseObject(BaseModel):
    name: str
    description: str
    interactions: Dict[str, Callable]
    data: Dict
    position: List[float] = [0, 0, 0]
    size: List[float] = [1, 1, 1]


class BaseWorld(BaseModel):
    name: str
    description: str
    objects: List[BaseObject]
    agents: List[GenerativeAgent]

    async def launch(self):
        await asyncio.gather(*(agent.autonomous_run() for agent in self.agents))

    def serialize_state(self):
        representation = {
            "name": self.name,
            "description": self.description,
            "objects": [obj.serialize_state() for obj in self.objects],
            "agents": [agent.serialize_state() for agent in self.agents],
        }
        return representation