from typing import List, Dict
from pydantic import BaseModel
from yeager_core.gen_agents.base_gen_agent import GenerativeAgent

"""
Required features:
- Positions and access to the agents
- Can add or remove agents in the pod
- Manages the pseudo-randomness and interactions of the agents
- Have critical elements such as library, blackboard, etc.
- Humans can only interact with agents through the pod, modifying the blackboard or adding/removing agents, etc.
"""

class ResearchPod(BaseModel):
    name: str
    description: str
    blackboard: List[str]
    agents: Dict[str,GenerativeAgent]
