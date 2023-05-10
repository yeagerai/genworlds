from typing import List
from yeager_core.events.base_event import Event


class AgentGetsNearbyEntitiesEvent(Event):
    event_type = "agent_gets_nearby_entities_event"
    description = "Get all entities near an agent."
    agent_id: str
    world_id: str


class WorldSendsNearbyEntitiesEvent(Event):
    event_type = "world_sends_nearby_entities_event"
    description = "Send all nearby entities to an agent."
    agent_id: str
    world_id: str
    nearby_entities: List


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
    

class EntityRequestWorldStateUpdateEvent(Event):
    event_type = "entity_request_world_state_update_event"
    description = "Request the latest world state update for an entity."
    entity_id: str
class EntityWorldStateUpdateEvent(Event):
    event_type = "entity_word_state_update_event"
    description = "Latest world state update for an entity."
    entity_id: str
    entity_world_state: str

