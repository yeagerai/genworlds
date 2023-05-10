from datetime import datetime
import threading
from uuid import uuid4
from typing import Generic, List, Type, TypeVar

from yeager_core.agents.yeager_autogpt.agent import YeagerAutoGPT
from yeager_core.objects.base_object import BaseObject
from yeager_core.sockets.world_socket_client import WorldSocketClient
from yeager_core.events.base_event import EventHandler, EventDict, Listener
from yeager_core.events.basic_events import (
    AgentGetsNearbyEntitiesEvent,
    EntityRequestWorldStateUpdateEvent,
    EntityWorldStateUpdateEvent,
    WorldSendsNearbyEntitiesEvent,
    WorldSendsSchemasEvent,
)
from yeager_core.worlds.world_entity import EntityTypeEnum, WorldEntity

WorldEntityType = TypeVar('WorldEntityType', bound=WorldEntity)
class BaseWorld(Generic[WorldEntityType]):
    entities: dict[str, WorldEntityType] = {}
    world_entity_constructor: Type[WorldEntityType]

    def __init__(
        self,
        world_entity_constructor: Type[WorldEntityType],
        name: str,
        description: str,
        event_dict: EventDict,
        event_handler: EventHandler,
        important_event_types: List[str],
    ):
        self.world_entity_constructor = world_entity_constructor

        self.important_event_types = important_event_types
        self.important_event_types.extend(
            [
                "agent_gets_nearby_entities_event",
                "entity_request_world_state_update_event",
            ]
        )
        self.event_dict = event_dict
        self.event_dict.register_events([AgentGetsNearbyEntitiesEvent, EntityRequestWorldStateUpdateEvent])

        self.event_handler = event_handler
        self.event_handler.register_listener(
            event_type="agent_gets_nearby_entities_event",
            listener=Listener(
                name="agent_gets_nearby_entities_event_listener",
                description="Listens for an agent requesting nearby objects",
                function=self.agent_gets_nearby_entities_listener,
            ),
        )
        self.event_handler.register_listener(
            event_type="entity_request_world_state_update_event",
            listener=Listener(
                name="entity_request_world_state_update_event_listener",
                description="Listens for an agent requesting their world state",
                function=self.entity_request_world_state_update_event_listener,
            ),
        )

        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.world_socket_client = WorldSocketClient(process_event=self.process_event, send_initial_event=self.world_sends_schemas)


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
        # All entities
        nearby_entities = self.get_nearby_entities(entity_id=event.agent_id)

        event = WorldSendsNearbyEntitiesEvent(
            agent_id=event.agent_id,
            world_id=self.id,
            created_at=datetime.now(),
            nearby_entities=nearby_entities,
        )
        self.world_socket_client.send_message(event.json())

    def get_agent_world_state_prompt(self, agent_id: str) -> str:
        agent_entity = self.get_agent_by_id(agent_id)

        world_state_prompt = (
            f"You are an agent in the world. You can do anything.\n"
        )

        return world_state_prompt

    def emit_agent_world_state(self, agent_id):
        world_state_prompt = self.get_agent_world_state_prompt(agent_id=agent_id)

        event = EntityWorldStateUpdateEvent(
            created_at=datetime.now(),
            entity_id=agent_id,
            entity_world_state=world_state_prompt,
        )

        self.world_socket_client.send_message(event.json())

    def entity_request_world_state_update_event_listener(
        self, event: EntityRequestWorldStateUpdateEvent
    ):
        self.emit_agent_world_state(agent_id=event.entity_id)

    def world_sends_schemas(self):
        schemas = []
        for obj in self.objects:
            for event in obj.event_dict.event_classes.values():
                schemas.append(event.schema_json(indent=2))

        for agent in self.agents:
            for event in agent.event_dict.event_classes.values():
                schemas.append(event.schema_json(indent=2))
        
        for event in self.event_dict.event_classes.values():
            schemas.append(event.schema_json(indent=2))

        world_info = WorldSendsSchemasEvent(
            world_id=self.id,
            world_name=self.name,
            world_description=self.description,
            created_at=datetime.now(),
            schemas=schemas,
            receiver_id="ALL",
        )        
        self.world_socket_client.send_message(world_info.json())

    def process_event(self, event):
        if (
            event["event_type"] in self.important_event_types
            # and event["world_id"] == self.id
        ):
            event_listener_name = event["event_type"]+"_listener"
            parsed_event = self.event_dict.get_event_class(
                event["event_type"]
            ).parse_obj(event)
            self.event_handler.handle_event(parsed_event, event_listener_name)


    def register_agent(self, agent: YeagerAutoGPT, **kwargs: WorldEntityType):
        entity: WorldEntityType = self.world_entity_constructor(
            id=agent.id,
            entity_type=EntityTypeEnum.AGENT,
            name=agent.ai_name,
            description=agent.description,
            **kwargs,
        )

        self.entities[entity.id] = entity

    def register_object(self, obj: BaseObject, **kwargs: WorldEntityType):
        entity: WorldEntityType = self.world_entity_constructor(
            id=obj.id,
            entity_type=EntityTypeEnum.OBJECT,
            name=obj.name,
            description=obj.description,
            **kwargs,
        )

        self.entities[entity.id] = entity


    def launch(self):
        threading.Thread(
            target=self.world_socket_client.websocket.run_forever,
            name=f"World {self.name} Thread",
            daemon=True,
        ).start()
