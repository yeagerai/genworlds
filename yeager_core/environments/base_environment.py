from typing import List, Dict, Callable, Any
from pydantic import BaseModel
from yeager_core.agents.base_gen_agent import GenerativeAgent


class BaseObject(BaseModel):
    name: str
    description: str
    interactions: Dict[str, Callable]
    data: Dict
    position: List[float] = [0, 0, 0]
    size: List[float] = [1, 1, 1]


class BaseEnvironment(BaseModel):
    name: str
    description: str
    objects: List[BaseObject]
    agents: List[GenerativeAgent]

    def run(self):
        for agent in self.agents:
            agent.run()
