from uuid import uuid4
from typing import Generic, Type, TypeVar, List


from genworlds.agents.base_agent.base_agent import BaseAgent
from genworlds.objects.base_object.base_object import BaseObject

from genworlds.worlds.base_world.events import (
    AgentGivesObjectToAgentEvent,
    AgentGetsAllEntitiesEvent,
    WorldSendsAllEntitiesEvent,
    EntityRequestWorldStateUpdateEvent,
    EntityWorldStateUpdateEvent,
    WorldSendsSchemasEvent,
)
from genworlds.worlds.base_world.base_world_entity import EntityTypeEnum, BaseWorldEntity

WorldEntityType = TypeVar("WorldEntityType", bound=BaseWorldEntity)


class BaseWorld(Generic[WorldEntityType], BaseObject):
    """
    Represents a basic simulated world environment.

    This class manages entities (agents and objects) within the simulated world, 
    keeps track of their states, and handles various world events. 
    The world communicates with entities using websockets and has capabilities 
    to register (add) agents and objects, emit world states to agents, and listen 
    to events from entities.

    Attributes:
        subconscious_event_classes (set[str]): Events that are processed without explicit triggering.
        entities (dict[str, WorldEntityType]): Dictionary of entities (agents/objects) managed by the world.
        entity_schemas (dict[str, dict]): Schema definitions for entities for serialization and validation.
        world_entity_constructor (Type[WorldEntityType]): Constructor to instantiate new world entity objects.

    Args:
        world_entity_constructor (Type[WorldEntityType]): Constructor to instantiate new world entity objects.
        name (str): Name of the world.
        description (str): Description or details about the world.
        id (str, optional): Unique identifier for the world. Defaults to a new UUID if not provided.
        websocket_url (str, optional): URL for the websocket communication. Defaults to "ws://127.0.0.1:7456/ws".

    Example:
        world = BaseWorld(MyEntityConstructor, "MyWorld", "A simple simulated world")
    """
    subconscious_event_classes: set[str]
    entities: dict[str, WorldEntityType]
    entity_schemas: dict[str, dict]
    world_entity_constructor: Type[WorldEntityType]

    def __init__(
        self,
        world_entity_constructor: Type[WorldEntityType],
        name: str,
        description: str,
        id: str = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        self.id = id if id else str(uuid4())
        self.name = name
        self.description = description
        self.world_entity_constructor = world_entity_constructor
        self.subconscious_event_classes = {
            AgentGetsAllEntitiesEvent,
            EntityRequestWorldStateUpdateEvent,
        }

        super().__init__(
            id=self.id,
            name=self.name,
            description=self.description,
            websocket_url=websocket_url,
        )

        self.entities = {}
        self.entity_schemas = {}

        self.register_event_listeners(
            [
                (
                    AgentGetsAllEntitiesEvent,
                    self.agent_gets_all_entities_listener,
                ),
                (
                    EntityRequestWorldStateUpdateEvent,
                    self.entity_request_world_state_update_event_listener,
                ),
                (
                    AgentGivesObjectToAgentEvent,
                    self.agent_gives_object_to_agent_listener,
                ),
            ]
        )

    def get_agent_by_id(self, agent_id: str) -> WorldEntityType:
        entity = self.entities.get(agent_id)
        if entity is None:
            raise Exception(f"Agent with id {agent_id} does not exist.")
        if entity.entity_type != EntityTypeEnum.AGENT:
            raise Exception(f"Entity with id {agent_id} is not an agent.")
        return entity

    def get_object_by_id(self, object_id: str) -> WorldEntityType:
        entity = self.entities.get(object_id)
        if entity is None:
            raise Exception(f"Object with id {object_id} does not exist.")
        if entity.entity_type != EntityTypeEnum.OBJECT:
            raise Exception(f"Entity with id {object_id} is not an object.")
        return entity

    ## Event Handlers

    def get_all_entities(self) -> dict:
        return self.entities

    def agent_gets_all_entities_listener(self, event: AgentGetsAllEntitiesEvent):
        self.emit_world_sends_all_entities(agent_id=event.sender_id)

    def emit_world_sends_all_entities(self, agent_id: str):
        all_entities = self.get_all_entities()
        self.send_event(
            WorldSendsAllEntitiesEvent,
            target_id=agent_id,
            all_entities=all_entities,
        )

    def get_agent_world_state_prompt(self, agent_id: str) -> str:
        agent_entity = self.get_agent_by_id(agent_id)
        world_state_prompt = (
            f"You are an agent in the world.\n" f"Your id is {agent_entity.id}.\n"
        )

        return world_state_prompt

    def emit_agent_world_state(self, agent_id):
        world_state_prompt = self.get_agent_world_state_prompt(agent_id=agent_id)

        self.send_event(
            EntityWorldStateUpdateEvent,
            target_id=agent_id,
            entity_world_state=world_state_prompt,
        )

    def entity_request_world_state_update_event_listener(
        self, event: EntityRequestWorldStateUpdateEvent
    ):
        self.world_sends_schemas()
        # self.world_sends_all_entities()
        self.emit_agent_world_state(agent_id=event.sender_id)
        self.emit_world_sends_all_entities(agent_id=event.sender_id)

    def agent_gives_object_to_agent_listener(self, event: AgentGivesObjectToAgentEvent):
        if event.object_id not in self.entities:
            raise Exception(f"Object with id {event.object_id} does not exist.")

        if event.recipient_agent_id not in self.entities:
            raise Exception(f"Agent with id {event.recipient_agent_id} does not exist.")

        if self.entities[event.object_id].held_by != event.sender_id:
            raise Exception(
                f"Object with id {event.object_id} is not held by agent with id {event.sender_id}."
            )

        self.entities[event.object_id].held_by = event.recipient_agent_id

        self.emit_world_sends_all_entities(agent_id=event.sender_id)
        self.emit_world_sends_all_entities(agent_id=event.recipient_agent_id)

    def world_sends_schemas(self):
        schemas = self.entity_schemas.copy()
        # Add world schemas
        events = {}
        for event_type, event in self.event_classes.items():
            if event not in self.subconscious_event_classes:
                events[event_type] = event.schema()

        schemas["World"] = events
        self.send_event(
            WorldSendsSchemasEvent,
            world_name=self.name,
            world_description=self.description,
            schemas=schemas,
        )

    def world_sends_all_entities(self):
        all_entities = self.entities.copy()
        self.send_event(WorldSendsAllEntitiesEvent, all_entities=[all_entities])

    def add_entity(self, entity, entity_type, **kwargs):
        class_name = entity.__class__.__name__

        if class_name not in self.entity_schemas:
            events = {}
            for event_type, event in entity.event_classes.items():
                events[event_type] = event.schema()
            self.entity_schemas[class_name] = events

        world_entity = self.world_entity_constructor(
            id=entity.id,
            entity_type=entity_type,
            entity_class=class_name,
            name=entity.name,
            description=entity.description,
            **kwargs,
        )
        self.entities[world_entity.id] = world_entity
        return world_entity

    def add_agent(self, agent: BaseAgent, **kwargs: WorldEntityType):
        entity = self.add_entity(agent, EntityTypeEnum.AGENT, **kwargs)
        print(f"Agent {entity} added to world.")
    
    def add_object(self, obj: BaseObject, **kwargs: WorldEntityType):
        entity = self.add_entity(obj, EntityTypeEnum.OBJECT, **kwargs)
        print(f"Object {entity} added to world.")
