from typing import List
from yeager_core.events.base_event import Event
from yeager_core.properties.basic_properties import Coordinates
from yeager_core.events.event_decorators import event_type


@event_type("agent_move_to_position")
class AgentMoveToPositionEvent(Event):
    description = "Move an agent to a position."
    agent_id: str
    new_position: Coordinates


@event_type("agent_gets_world_objects_in_radius")
class AgentGetsWorldObjectsInRadiusEvent(Event):
    description = "Get all objects in a radius around an agent."
    agent_id: str
    world_id: str
    current_agent_position: Coordinates
    radius: int


@event_type("world_sends_objects_in_radius")
class WorldSendsObjectsInRadiusEvent(Event):
    description = "Send all objects in a radius around an agent."
    agent_id: str
    world_id: str
    object_ids_in_radius: List[str]


@event_type("agent_gets_object_info")
class AgentGetsObjectInfoEvent(Event):
    description = "Get info about an object."
    agent_id: str
    object_id: str


class AgentGetsAgentInfoEvent(Event):
    description = "Get info about an agent."
    agent_id: str
    target_agent_id: str


@event_type("object_sends_info_to_agent")
class ObjectSendsInfoToAgentEvent(Event):
    description = "Send info about an object to an agent."
    agent_id: str
    object_id: str
    object_name: str
    object_description: str
    possible_events: List[Event]


@event_type("agent_interacts_with_object")
class AgentInteractsWithObject(Event):
    description = "An agent interacts with an object."
    agent_id: str
    object_id: str
    event: Event


class AgentGetsWorldAgentsInRadiusEvent(Event):
    description = "Get all agents in a radius around an agent."
    agent_id: str
    world_id: str
    current_agent_position: Coordinates
    radius: int


class AgentSpeaksWithAgentEvent(Event):
    description = "An agent speaks with another agent."
    agent_id: str
    other_agent_id: str
    message: str
