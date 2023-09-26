from typing import List, Type

from genworlds.events.abstracts.action import AbstractAction
from genworlds.worlds.abstracts.world import AbstractWorld
from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.worlds.concrete.community_chat_interface.actions import (
    WorldSendsScreensToUser,
)
from genworlds.worlds.concrete.base.actions import (
    WorldSendsAvailableEntities,
    WorldSendsAvailableActionSchemas,
)


class ChatInterfaceWorld(AbstractWorld):
    def __init__(
        self,
        name: str,
        description: str,
        agents: List[AbstractAgent] = [],
        objects: List[AbstractObject] = [],
        actions: List[Type[AbstractAction]] = [],
        id: str = None,
        screens_config_path: str = "./screens_config.json",
    ):
        self.screens_config_path = screens_config_path
        # availability = all entities
        get_available_entities = WorldSendsAvailableEntities(host_object=self)
        get_available_action_schemas = WorldSendsAvailableActionSchemas(
            host_object=self
        )
        actions.append(get_available_entities)
        actions.append(get_available_action_schemas)
        actions.append(WorldSendsScreensToUser(host_object=self))

        super().__init__(
            name=name,
            description=description,
            agents=agents,
            objects=objects,
            actions=actions,
            get_available_entities=get_available_entities,
            get_available_action_schemas=get_available_action_schemas,
            id=id,
        )
