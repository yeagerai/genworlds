from uuid import uuid4
from typing import List, Type
from genworlds.events.abstracts.action import AbstractAction

from genworlds.worlds.abstracts.world import AbstractWorld
from genworlds.worlds.abstracts.world_entity import AbstractWorldEntity
from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.objects.abstracts.object import AbstractObject

from genworlds.worlds.concrete.base.actions import (
    WorldSendsAvailableEntities,
    WorldSendsAvailableActionSchemas,
)

class BaseWorld(AbstractWorld):

    def __init__(
        self,
        name: str,
        description: str,
        agents: List[AbstractAgent] = [],
        objects: List[AbstractObject] = [],
        actions: List[Type[AbstractAction]] = [],
        id: str = None,
    ):
        # availability = all entities
        get_available_entities = WorldSendsAvailableEntities(host_object=self)
        get_available_action_schemas = WorldSendsAvailableActionSchemas(host_object=self)
        actions.append(get_available_entities)
        actions.append(get_available_action_schemas)

        super().__init__(
            id=id,
            name=name,
            description=description,
            agents=agents,
            objects=objects,
            actions=actions,
            get_available_entities=get_available_entities,
            get_available_action_schemas=get_available_action_schemas,
        )

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

