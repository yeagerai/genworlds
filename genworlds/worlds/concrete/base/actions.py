from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.events.abstracts.action import AbstractAction


class AgentWantsUpdatedStateEvent(AbstractEvent):
    event_type = "agent_wants_updated_state"
    description = "Agent wants to update its state."
    # that gives available_action_schemas, and available_entities


class WorldSendsAvailableEntitiesEvent(AbstractEvent):
    event_type = "world_sends_available_entities_event"
    description = "Send available entities."
    available_entities: dict


class WorldSendsAvailableEntities(AbstractAction):
    trigger_event_class = AgentWantsUpdatedStateEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentWantsUpdatedStateEvent):
        self.host_object.update_entities()
        all_entities = self.host_object.entities
        event = WorldSendsAvailableEntitiesEvent(
            sender_id=self.host_object.id,
            available_entities=all_entities,
            target_id=event.sender_id,
        )
        self.host_object.send_event(event)


class WorldSendsAvailableActionSchemasEvent(AbstractEvent):
    event_type = "world_sends_available_action_schemas_event"
    description = "The world sends the possible action schemas to all the agents."
    world_name: str
    world_description: str
    available_action_schemas: dict[str, dict]


class WorldSendsAvailableActionSchemas(AbstractAction):
    trigger_event_class = AgentWantsUpdatedStateEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentWantsUpdatedStateEvent):
        self.host_object.update_action_schemas()
        all_action_schemas = self.host_object.action_schemas
        event = WorldSendsAvailableActionSchemasEvent(
            sender_id=self.host_object.id,
            world_name=self.host_object.name,
            world_description=self.host_object.description,
            available_action_schemas=all_action_schemas,
        )
        self.host_object.send_event(event)


class AgentSpeaksWithAgentEvent(AbstractEvent):
    event_type = "agent_speaks_with_agent_event"
    description = "An agent speaks with another agent."
    message: str

class AgentSpeaksWithAgent(AbstractAction):
    trigger_event_class = AgentSpeaksWithAgentEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentSpeaksWithAgentEvent):
        self.host_object.send_event(event)

class UserSpeaksWithAgentEvent(AbstractEvent):
    event_type = "user_speaks_with_agent_event"
    description = "The user speaks with an agent."
    message: str

class AgentSpeaksWithUserEvent(AbstractEvent):
    event_type = "agent_speaks_with_user_event"
    description = "An agent speaks with the user."
    message: str

class AgentSpeaksWithUser(AbstractAction):
    trigger_event_class = AgentSpeaksWithUserEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentSpeaksWithUserEvent):
        self.host_object.send_event(event)    

# class AgentGivesObjectToAgentEvent(AbstractEvent):
#     event_type = "agent_gives_object_to_agent_event"
#     description = """Give an object from your inventory to another agent.
# Only the holder of an item can use this event, you cannot use this event to request an item.
# Target id must be the id of the world."""
#     object_id: str
#     recipient_agent_id: str

# class EntityRequestWorldStateUpdateEvent(AbstractEvent):
#     event_type = "entity_request_world_state_update_event"
#     description = "Request the latest world state update for an entity."

# class EntityWorldStateUpdateEvent(AbstractEvent):
#     event_type = "entity_world_state_update_event"
#     description = "Latest world state update for an entity."
#     entity_world_state: str
