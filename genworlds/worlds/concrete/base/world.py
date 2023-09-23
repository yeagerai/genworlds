from uuid import uuid4
from typing import List
from genworlds.events.abstracts.action import AbstractAction

from genworlds.worlds.abstracts.world import AbstractWorld
from genworlds.worlds.abstracts.world_entity import AbstractWorldEntity
from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.objects.abstracts.object import AbstractObject

from genworlds.worlds.concrete.base.actions import (
    WorldSendsAllEntities,
    WorldSendsActionSchemas,
)

class BaseWorld(AbstractWorld):

    subconscious_event_classes: set[str]
    entities: dict[str, AbstractWorldEntity]
    action_schemas: dict[str, dict]

    def __init__(
        self,
        name: str,
        description: str,
        agents: List[AbstractAgent] = [],
        objects: List[AbstractObject] = [],
        id: str = None,
    ):
        self._id = id if id else str(uuid4())
        self._host_world_id = self.id
        self._name = name
        self._description = description
        self._agents = agents
        self._objects = objects
        self._get_available_entities = WorldSendsAllEntities(host_object=self)
        self._get_available_action_schemas = WorldSendsActionSchemas(host_object=self)
        self._actions = [
            self.get_available_entities,
        ]

        super().__init__(
            id=self._id,
            actions=self._actions,
        )

        self.update_entities()
        self.update_action_schemas()

    def update_entities(self):
        self.entities = {}
        self.entities[self.id] = self.get_entity_from_obj(self)
        for agent in self.agents:
            self.entities[agent.id] = self.get_entity_from_obj(agent)

        for obj in self.objects:
            self.entities[obj.id] = self.get_entity_from_obj(obj)

    def update_action_schemas(self):
        self.action_schemas = {}
        for action in self.actions:
            event_type = action.trigger_event_class.__fields__["event_type"].default
            self.action_schemas[type(self).__name__ + event_type] = action.trigger_event_class.schema()
        for obj in self.objects:
            for action in obj.actions:
                event_type = action.trigger_event_class.__fields__["event_type"].default
                self.action_schemas[type(obj).__name__ + event_type] = action.trigger_event_class.schema()
        for agent in self.agents:
            for action in agent.actions:
                event_type = action.trigger_event_class.__fields__["event_type"].default
                self.action_schemas[type(agent).__name__ + event_type] = action.trigger_event_class.schema()

    @property
    def id(self) -> str:
        return self._id
    
    @property
    def host_world_id(self) -> str:
        return self._host_world_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def agents(self) -> List[AbstractAgent]:
        return self._agents
    
    @property
    def objects(self) -> List[AbstractObject]:
        return self._objects
    
    @property
    def get_available_entities(self):
        # all entities (simple availability concept, everything is available)
        return self._get_available_entities

    @property
    def get_available_action_schemas(self):
        # all entities (simple availability concept, everything is available)
        return self._get_available_action_schemas

    @property
    def actions(self) -> List[AbstractAction]:
        return self._actions


    # def get_agent_world_state_prompt(self, agent_id: str) -> str:
    #     agent_entity = self.get_agent_by_id(agent_id)
    #     world_state_prompt = (
    #         f"You are an agent in the world.\n" f"Your id is {agent_entity.id}.\n"
    #     )

    #     return world_state_prompt

    # def emit_agent_world_state(self, agent_id):
    #     world_state_prompt = self.get_agent_world_state_prompt(agent_id=agent_id)

    #     self.send_event(
    #         EntityWorldStateUpdateEvent,
    #         target_id=agent_id,
    #         entity_world_state=str(world_state_prompt),
    #     )

    # def entity_request_world_state_update_event_listener(
    #     self, event: EntityRequestWorldStateUpdateEvent
    # ):
    #     self.world_sends_schemas()
    #     # self.world_sends_all_entities()
    #     self.emit_agent_world_state(agent_id=event.sender_id)
    #     self.emit_world_sends_all_entities(agent_id=event.sender_id)

    # def world_sends_schemas(self):
    #     schemas = self.entity_schemas.copy()
    #     # Add world schemas
    #     events = {}
    #     for event_type, event in self.event_classes.items():
    #         if event not in self.subconscious_event_classes:
    #             events[event_type] = event.schema()

    #     schemas["World"] = events
    #     self.send_event(
    #         WorldSendsSchemasEvent,
    #         world_name=self.name,
    #         world_description=self.description,
    #         schemas=schemas,
    #     )

