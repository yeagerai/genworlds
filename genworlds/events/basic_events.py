from genworlds.events import BaseEvent


class AgentGetsNearbyEntitiesEvent(BaseEvent):
    event_type = "agent_gets_nearby_entities_event"
    description = "Get all entities near an agent."


class WorldSendsNearbyEntitiesEvent(BaseEvent):
    event_type = "world_sends_nearby_entities_event"
    description = "Send all nearby entities to an agent."
    nearby_entities: list


class WorldSendsAllEntitiesEvent(BaseEvent):
    event_type = "world_sends_all_entities_event"
    description = "Send all entities."
    all_entities: list


class AgentGetsObjectInfoEvent(BaseEvent):
    event_type = "agent_gets_object_info_event"
    description = "Get info about an object."


class AgentGetsAgentInfoEvent(BaseEvent):
    event_type = "agent_gets_agent_info_event"
    description = "Get info about an agent."


class ObjectSendsInfoToAgentEvent(BaseEvent):
    event_type = "object_sends_info_to_agent_event"
    description = "Send info about an object to an agent."
    object_id: str
    object_name: str
    object_description: str
    possible_events: list[BaseEvent]


class AgentSpeaksWithAgentEvent(BaseEvent):
    event_type = "agent_speaks_with_agent_event"
    description = "An agent speaks with another agent."
    message: str

class AgentSpeaksWithUserEvent(BaseEvent):
    event_type = "agent_speaks_with_user_event"
    description = "An agent speaks with the user."
    message: str

class UserSpeaksWithAgentEvent(BaseEvent):
    event_type = "user_speaks_with_agent_event"
    description = "The user speaks with an agent."
    message: str


class WorldSendsSchemasEvent(BaseEvent):
    event_type = "world_sends_schemas_event"
    description = "The world sends the possible interactions to all the agents."
    world_name: str
    world_description: str
    schemas: dict[str, dict]


class EntityRequestWorldStateUpdateEvent(BaseEvent):
    event_type = "entity_request_world_state_update_event"
    description = "Request the latest world state update for an entity."


class EntityWorldStateUpdateEvent(BaseEvent):
    event_type = "entity_world_state_update_event"
    description = "Latest world state update for an entity."
    entity_world_state: str


class AgentGivesObjectToAgentEvent(BaseEvent):
    event_type = "agent_gives_object_to_agent_event"
    description = "Give an object from your inventory to another agent. Only the holder of an item can use this event, you cannot use this event to request an item. Target id must be the id of the world."
    object_id: str
    recipient_agent_id: str
