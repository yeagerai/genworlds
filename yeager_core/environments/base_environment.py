from typing import List, Dict, Callable, Any
from pydantic import BaseModel
from yeager_core.agents.base_gen_agent import GenerativeAgent

"""
Required features:
- Positions and access to the agents
- Can add or remove agents in the pod
- Manages the pseudo-randomness and interactions of the agents
- Have critical elements such as library, blackboard, etc.
- Humans can only interact with agents through the pod, modifying the blackboard or adding/removing agents, etc.
"""

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
    agents: Dict[str, GenerativeAgent]
