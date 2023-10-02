from typing import Dict, List, Set, Any, Optional
from pydantic import BaseModel, Field
from genworlds.events.abstracts.event import AbstractEvent


class AbstractAgentState(BaseModel):
    """
    ### Serialize to JSON
    json_representation = instance.json()

    ### Deserialize from JSON
    instance = AbstractAgentState.parse_raw(json_representation)
    """

    # Static initialized in the constructor
    id: str = Field(..., description="Unique identifier of the agent.")
    description: str = Field(..., description="Description of the agent.")
    name: str = Field(..., description="Name of the agent.")
    host_world_prompt: str = Field(..., description="Prompt of the host world.")
    simulation_memory_persistent_path: Optional[str] = Field(
        None, description="Memory object storing the simulation data."
    )
    memory_ignored_event_types: Set[str] = Field(
        ...,
        description="Set of event types that will be ignored and not added to memory of the agent.",
    )
    wakeup_event_types: Set[str] = Field(
        ..., description="Events that can wake up the agent."
    )
    action_schema_chains: List[List[str]] = Field(
        ...,
        description="List of action schema chains that inhibit the action selector.",
    )
    goals: List[str] = Field(..., description="List of goals of the agent.")

    # Dynamically updated, so during one think_n_do cycle all of these must be updated somehow
    plan: List[str] = Field(..., description="List of actions that form the plan.")
    last_retrieved_memory: str = Field(
        ..., description="Last retrieved memory of the agent."
    )
    other_thoughts_filled_parameters: Dict[str, str] = Field(
        ..., description="Parameters filled by other thoughts."
    )
    available_action_schemas: Dict[str, Any] = Field(
        ..., description="Available action schemas with their descriptions."
    )
    available_entities: List[str] = Field(
        ..., description="List of available entities in the environment."
    )
    is_asleep: bool = Field(..., description="Indicates whether the agent is asleep.")
    current_action_chain: List[str] = Field(
        ..., description="List of action schemas that are currently being executed."
    )
