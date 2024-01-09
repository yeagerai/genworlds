from typing import NamedTuple, Dict, List, Any, Optional, Callable, Union
from datetime import datetime

class Event(NamedTuple):
    sender_id: str
    target_id: str
    created_at: Union[str, datetime]
    event_type: str
    data: Dict

class EntityState(NamedTuple):
    id: str
    name: str
    description: str
    sub_types: List[str]
    vars: Dict[str, Any]
    custom_state_updaters: Optional[List[Callable]]
    actions: Dict[str, Callable]

class AgentState(NamedTuple):
    id: str
    name: str
    description: str
    sub_types: List[str]
    memories: List[Any]
    plan: str
    goals: List[str]
    llm_platform: str
    model_name: str
    endpoint: str
    vars: Dict[str, Any]
    custom_state_updaters: Optional[List[Callable]]
    actions: Dict[str, Callable]

class WorldState(NamedTuple):
    id: str
    name: str
    description: str
    sub_types: List[str]
    agent_states: Dict[str, AgentState]
    entity_states: Dict[str, EntityState]
    event_history: List[Event]
    vars: Dict[str, Any]
    custom_state_updaters: Optional[List[Callable]]
    actions: Dict[str, Callable]
