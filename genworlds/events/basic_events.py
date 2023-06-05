from genworlds.events.websocket_event_handler import Event


class AgentGetsNearbyEntitiesEvent(Event):
    event_type = "agent_gets_nearby_entities_event"
    description = "Get all entities near an agent."


class WorldSendsNearbyEntitiesEvent(Event):
    event_type = "world_sends_nearby_entities_event"
    description = "Send all nearby entities to an agent."
    nearby_entities: list


class AgentGetsObjectInfoEvent(Event):
    event_type = "agent_gets_object_info_event"
    description = "Get info about an object."


class AgentGetsAgentInfoEvent(Event):
    event_type = "agent_gets_agent_info_event"
    description = "Get info about an agent."


class ObjectSendsInfoToAgentEvent(Event):
    event_type = "object_sends_info_to_agent_event"
    description = "Send info about an object to an agent."
    object_id: str
    object_name: str
    object_description: str
    possible_events: list[Event]


class AgentSpeaksWithAgentEvent(Event):
    event_type = "agent_speaks_with_agent_event"
    description = "An agent speaks with another agent."
    message: str


class WorldSendsSchemasEvent(Event):
    event_type = "world_sends_schemas_event"
    description = "The world sends the possible interactions to all the agents."
    world_name: str
    world_description: str
    schemas: dict[str, dict]


class EntityRequestWorldStateUpdateEvent(Event):
    event_type = "entity_request_world_state_update_event"
    description = "Request the latest world state update for an entity."


class EntityWorldStateUpdateEvent(Event):
    event_type = "entity_world_state_update_event"
    description = "Latest world state update for an entity."
    entity_world_state: str


class AgentGivesObjectToAgentEvent(Event):
    event_type = "agent_gives_object_to_agent_event"
    description = "Give an object from your inventory to another agent. Only the holder of an item can use this event, you cannot use this event to request an item. Target id must be the id of the world."
    object_id: str
    recipient_agent_id: str
