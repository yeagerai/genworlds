from uuid import uuid4
from typing import Generic, Type, TypeVar

import uvicorn

from genworlds.agents.yeager_autogpt.agent import YeagerAutoGPT
from genworlds.objects.base_object import BaseObject
from genworlds.events.websocket_event_handler import WebsocketEventHandler
from genworlds.events.basic_events import (
    AgentGetsNearbyEntitiesEvent,
    AgentGivesObjectToAgentEvent,
    AgentSpeaksWithAgentEvent,
    EntityRequestWorldStateUpdateEvent,
    EntityWorldStateUpdateEvent,
    WorldSendsNearbyEntitiesEvent,
    WorldSendsSchemasEvent,
)
from genworlds.worlds.base_world_entity import EntityTypeEnum, BaseWorldEntity

WorldEntityType = TypeVar('WorldEntityType', bound=BaseWorldEntity)
class BaseWorld(Generic[WorldEntityType], WebsocketEventHandler):
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
        self.subconscious_event_classes = {AgentGetsNearbyEntitiesEvent, EntityRequestWorldStateUpdateEvent}

        super().__init__(self.id, websocket_url=websocket_url)

        self.entities = {}
        self.entity_schemas = {}

        self.register_event_listeners([
            (AgentGetsNearbyEntitiesEvent, self.agent_gets_nearby_entities_listener),
            (EntityRequestWorldStateUpdateEvent, self.entity_request_world_state_update_event_listener),
            (AgentGivesObjectToAgentEvent, self.agent_gives_object_to_agent_listener),
        ])


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

    def get_nearby_entities(self, entity_id: str) -> WorldEntityType:
        # Check if reference entity exists
        self.entities.get(entity_id)
        
        # All entities
        return self.entities 

    def agent_gets_nearby_entities_listener(
        self, event: AgentGetsNearbyEntitiesEvent
    ):
        self.emit_world_sends_nearby_entities(agent_id=event.agent_id)        

    def emit_world_sends_nearby_entities(self, agent_id: str):
        nearby_entities = self.get_nearby_entities(agent_id)

        self.send_event(WorldSendsNearbyEntitiesEvent,
            target_id=agent_id,
            nearby_entities=nearby_entities
        )

    def get_agent_world_state_prompt(self, agent_id: str) -> str:
        agent_entity = self.get_agent_by_id(agent_id)

        world_state_prompt = (
            f"You are an agent in the world.\n"
            f"Your id is {agent_entity.id}.\n"
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
        self.emit_agent_world_state(agent_id=event.sender_id)
        self.world_sends_schemas()
        self.emit_world_sends_nearby_entities(agent_id=event.sender_id) 


    def agent_gives_object_to_agent_listener(
        self, event: AgentGivesObjectToAgentEvent
    ):
        if event.object_id not in self.entities:
            raise Exception(f"Object with id {event.object_id} does not exist.")
        
        if event.recipient_agent_id not in self.entities:
            raise Exception(f"Agent with id {event.recipient_agent_id} does not exist.")
        
        if self.entities[event.object_id].held_by != event.sender_id:
            raise Exception(f"Object with id {event.object_id} is not held by agent with id {event.sender_id}.")

        self.entities[event.object_id].held_by = event.recipient_agent_id 

        self.emit_world_sends_nearby_entities(agent_id=event.sender_id)    
        self.emit_world_sends_nearby_entities(agent_id=event.recipient_agent_id)    

    def world_sends_schemas(self):
        schemas = self.entity_schemas.copy()
        # Add world schemas
        events = {}
        for (event_type, event) in self.event_classes.items():
            if event not in self.subconscious_event_classes:
                events[event_type] = event.schema()

        schemas['World'] = events      
        self.send_event(
            WorldSendsSchemasEvent,
            world_name=self.name,
            world_description=self.description,
            schemas=schemas,
        )

    def register_agent(self, agent: YeagerAutoGPT, **kwargs: WorldEntityType):
        class_name = agent.__class__.__name__

        if (class_name not in self.entity_schemas):
            events = {}

            # for event_class in agent.interesting_events:
            #     events[event_class.__fields__['event_type'].default] = event_class.schema()

            self.entity_schemas[class_name] = events

        entity: WorldEntityType = self.world_entity_constructor(
            id=agent.id,
            entity_type=EntityTypeEnum.AGENT,
            entity_class=class_name,
            name=agent.ai_name,
            description=agent.description,
            events=self.entity_schemas[class_name],
            **kwargs,
        )

        print("Registered agent", entity)

        self.entities[entity.id] = entity

    def register_object(self, obj: BaseObject, **kwargs: WorldEntityType):
        class_name = obj.__class__.__name__

        if (class_name not in self.entity_schemas):
            events = {}
            for (event_type, event) in obj.event_classes.items():
                events[event_type] = event.schema()

            self.entity_schemas[class_name] = events

        entity: WorldEntityType = self.world_entity_constructor(
            id=obj.id,
            entity_type=EntityTypeEnum.OBJECT,
            entity_class=class_name,
            name=obj.name,
            description=obj.description,
            **kwargs,
        )

        print("Registered object", entity)

        self.entities[entity.id] = entity

    
