from typing import Dict, List, Set, Any, Optional
from pydantic import BaseModel, Field
from genworlds.events.abstracts.event import AbstractEvent

class AbstractAgentState(BaseModel):
    """
    # Serialize to JSON
    json_representation = instance.json()

    # Deserialize from JSON
    instance = AbstractAgentState.parse_raw(json_representation)
    """

    id: str = Field(..., description="Unique identifier of the agent.")
    available_action_schemas: Dict[str, Any] = Field(..., description="Available action schemas with their descriptions.")
    available_entities: List[str] = Field(..., description="List of available entities in the environment.")
    simulation_memory_persistent_path: Optional[str] = Field(None, description="Memory object storing the simulation data.")
    important_event_types: Set[str] = Field(..., description="Set of event types considered important by the agent.")
    interesting_event_types: Set[str] = Field(..., description="Set of events considered interesting by the agent.")
    wakeup_event_types: Set[str] = Field(..., description="Events that can wake up the agent.")
    is_asleep: bool = Field(..., description="Indicates whether the agent is asleep.")
    all_events: List[AbstractEvent] = Field(..., description="List of all events the agent is aware of.")
    last_events: List[AbstractEvent] = Field(..., description="List of the most recent events the agent is aware of.")
