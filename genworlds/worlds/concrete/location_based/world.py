from typing import List, Type
from genworlds.worlds.abstracts.world import AbstractWorld
from genworlds.worlds.abstracts.world_entity import AbstractWorldEntity
from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.action import AbstractAction

from genworlds.worlds.concrete.location_based.actions import (
    WorldSendsSameLocationEntities,
    WorldSendsSameLocationActionSchemas,
    WorldSetsAgentLocation,
)


class WorldLocationEntity(AbstractWorldEntity):
    location: str = None


class LocationWorld(AbstractWorld[WorldLocationEntity]):
    locations: list[str] = []

    def __init__(
        self,
        name: str,
        description: str,
        locations: list[str],
        agents: List[AbstractAgent] = [],
        objects: List[AbstractObject] = [],
        actions: List[Type[AbstractAction]] = [],
        id: str = None,
    ):
        self.locations = locations
        # availability = same location as sender id
        get_available_entities = WorldSendsSameLocationEntities(host_object=self)
        get_available_action_schemas = WorldSendsSameLocationActionSchemas(
            host_object=self
        )

        actions.append(get_available_entities)
        actions.append(get_available_action_schemas)
        actions.append(WorldSetsAgentLocation(host_object=self))

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

    def add_location(self, location: str):
        self.locations.append(location)

    def remove_location(self, location: str):
        self.locations.remove(location)
