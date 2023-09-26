from typing import List, Dict
from genworlds.agents.abstracts.agent_state import AbstractAgentState


class BasicAssistantState(AbstractAgentState):
    ### Revisar para que son

    constraints: List[str]
    evaluation_principles: List[str]

    ### No en el Basic Assistant

    role: str  # roundtable
    background: str  # roundtable
    personality: str  # roundtable
    personality_db: List[str]  # roundtable
    topic_of_conversation: str  # roundtable
