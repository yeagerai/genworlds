from typing import List
import json

from genworlds.worlds.concrete.base.world import BaseWorld
from genworlds.worlds.abstracts.world_entity import AbstractWorldEntity
from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.worlds.concrete.community_chat_interface.actions import (
    WorldSendsScreensToUser,
)

class ChatInterfaceWorld(BaseWorld):

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
        screens_config_path: str = "./screens_config.json",
    ):
        super().__init__(
            name=name,
            description=description,
            agents=agents,
            objects=objects,
            id=id,
        )

        self.screens_config_path = screens_config_path
        self.actions.append(WorldSendsScreensToUser(host_object=self))