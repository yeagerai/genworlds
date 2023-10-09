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
    description = "Send available entities."

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
    available_action_schemas: dict[str, str]


class WorldSendsAvailableActionSchemas(AbstractAction):
    trigger_event_class = AgentWantsUpdatedStateEvent
    description = "The world sends the possible action schemas to all the agents."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentWantsUpdatedStateEvent):
        self.host_object.update_action_schemas()
        self.host_object.update_entities()
        all_action_schemas = self.host_object.action_schemas
        all_entities = self.host_object.entities
        to_delete = []
        for action_schema in all_action_schemas:
            if all_entities[action_schema.split(":")[0]].entity_type == "AGENT" and action_schema.split(":")[0] != event.sender_id:
                to_delete.append(action_schema)

            if all_entities[action_schema.split(":")[0]].entity_type == "WORLD":
                to_delete.append(action_schema)
        
            if action_schema == f"{event.sender_id}:AgentListensEvents":
                to_delete.append(action_schema)

        for action_schema in to_delete:
            del all_action_schemas[action_schema]
            
        event = WorldSendsAvailableActionSchemasEvent(
            sender_id=self.host_object.id,
            world_name=self.host_object.name,
            world_description=self.host_object.description,
            available_action_schemas=all_action_schemas,
        )
        self.host_object.send_event(event)


class UserSpeaksWithAgentEvent(AbstractEvent):
    event_type = "user_speaks_with_agent_event"
    description = "The user speaks with an agent."
    message: str
