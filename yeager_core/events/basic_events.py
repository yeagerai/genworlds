from typing import List
from yeager_core.events.base_event import Event
from yeager_core.properties.basic_properties import Coordinates


class AgentMoveToPositionEvent(Event):
    event_type = "agent_move_to_position_event"
    description = "Move an agent to a position."
    agent_id: str
    new_position: Coordinates


class AgentGetsWorldObjectsInRadiusEvent(Event):
    event_type = "agent_gets_world_objects_in_radius_event"
    description = "Get all objects in a radius around an agent."
    agent_id: str
    world_id: str
    current_agent_position: Coordinates
    radius: int


class WorldSendsObjectsInRadiusEvent(Event):
    event_type = "world_sends_objects_in_radius_event"
    description = "Send all objects in a radius around an agent."
    agent_id: str
    world_id: str
    object_ids_in_radius: List[str]


class AgentGetsObjectInfoEvent(Event):
    event_type = "agent_gets_object_info_event"
    description = "Get info about an object."
    agent_id: str
    object_id: str


class AgentGetsAgentInfoEvent(Event):
    event_type = "agent_gets_agent_info_event"
    description = "Get info about an agent."
    agent_id: str
    target_agent_id: str


class ObjectSendsInfoToAgentEvent(Event):
    event_type = "object_sends_info_to_agent_event"
    description = "Send info about an object to an agent."
    agent_id: str
    object_id: str
    object_name: str
    object_description: str
    possible_events: List[Event]


class AgentInteractsWithObject(Event):
    event_type = "agent_interacts_with_object_event"
    description = "An agent interacts with an object."
    agent_id: str
    object_id: str
    event: Event


class AgentGetsWorldAgentsInRadiusEvent(Event):
    event_type = "agent_gets_world_agents_in_radius_event"
    description = "Get all agents in a radius around an agent."
    agent_id: str
    current_agent_position: Coordinates
    radius: int


class AgentSpeaksWithAgentEvent(Event):
    event_type = "agent_speaks_with_agent_event"
    description = "An agent speaks with another agent."
    agent_id: str
    other_agent_id: str
    message: str

class WorldSendsSchemasEvent(Event):
    event_type = "world_sends_schemas_event"
    description = "The world sends the possible interactions to all the agents."
    receiver_id = "ALL AGENTS"
    world_id: str
    world_name: str
    world_description: str
    schemas:List[str]
    