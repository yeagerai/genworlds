from genworlds.events.abstracts.event import AbstractEvent


class AgentGetsAllEntitiesEvent(AbstractEvent):
    event_type = "agent_gets_nearby_entities_event"
    description = "Get all entities near an agent."


class AgentGetsNearbyEntitiesEvent(AbstractEvent):
    event_type = "agent_gets_nearby_entities_event"
    description = "Get all entities near an agent."


class WorldSendsNearbyEntitiesEvent(AbstractEvent):
    event_type = "world_sends_nearby_entities_event"
    description = "Send all nearby entities to an agent."
    nearby_entities: list


class WorldSendsAllEntitiesEvent(AbstractEvent):
    event_type = "world_sends_all_entities_event"
    description = "Send all entities."
    all_entities: dict


class AgentGetsObjectInfoEvent(AbstractEvent):
    event_type = "agent_gets_object_info_event"
    description = "Get info about an object."


class AgentGetsAgentInfoEvent(AbstractEvent):
    event_type = "agent_gets_agent_info_event"
    description = "Get info about an agent."


class ObjectSendsInfoToAgentEvent(AbstractEvent):
    event_type = "object_sends_info_to_agent_event"
    description = "Send info about an object to an agent."
    object_id: str
    object_name: str
    object_description: str
    possible_events: list[AbstractEvent]


class AgentSpeaksWithAgentEvent(AbstractEvent):
    event_type = "agent_speaks_with_agent_event"
    description = "An agent speaks with another agent."
    message: str


class AgentSpeaksWithUserEvent(AbstractEvent):
    event_type = "agent_speaks_with_user_event"
    description = "An agent speaks with the user."
    message: str


class UserSpeaksWithAgentEvent(AbstractEvent):
    event_type = "user_speaks_with_agent_event"
    description = "The user speaks with an agent."
    message: str


class WorldSendsSchemasEvent(AbstractEvent):
    event_type = "world_sends_schemas_event"
    description = "The world sends the possible interactions to all the agents."
    world_name: str
    world_description: str
    schemas: dict[str, dict]


class EntityRequestWorldStateUpdateEvent(AbstractEvent):
    event_type = "entity_request_world_state_update_event"
    description = "Request the latest world state update for an entity."


class EntityWorldStateUpdateEvent(AbstractEvent):
    event_type = "entity_world_state_update_event"
    description = "Latest world state update for an entity."
    entity_world_state: str


class AgentGivesObjectToAgentEvent(AbstractEvent):
    event_type = "agent_gives_object_to_agent_event"
    description = """Give an object from your inventory to another agent. 
Only the holder of an item can use this event, you cannot use this event to request an item. 
Target id must be the id of the world."""
    object_id: str
    recipient_agent_id: str
