from __future__ import annotations

from typing import Generic, TypeVar, List, Type
from time import sleep
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.worlds.abstracts.world_entity import AbstractWorldEntity

from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.events.abstracts.action import AbstractAction
from genworlds.simulation.sockets.server import start_thread as socket_server_start

WorldEntityType = TypeVar("WorldEntityType", bound=AbstractWorldEntity)


class AbstractWorld(Generic[WorldEntityType], AbstractObject):
    """
    An interface class representing a generic world in the simulation.
    """

    entities: dict[str, AbstractWorldEntity]
    action_schemas: dict[str, dict]

    def __init__(
        self,
        name: str,
        id: str,
        description: str,
        actions: List[Type[AbstractAction]],
        objects: List[AbstractObject],
        agents: List[AbstractAgent],
        get_available_entities: AbstractAction,
        get_available_action_schemas: AbstractAction,
    ):
        self.objects = objects
        self.agents = agents
        self.get_available_entities = get_available_entities
        self.get_available_action_schemas = get_available_action_schemas
        super().__init__(
            name=name, id=id, description=description, host_world_id=id, actions=actions
        )

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
            key, value = action.action_schema
            self.action_schemas[key] = value
        for obj in self.objects:
            for action in obj.actions:
                key, value = action.action_schema
                self.action_schemas[key] = value
        for agent in self.agents:
            for action in agent.actions:
                key, value = action.action_schema
                self.action_schemas[key] = value

    def get_entity_from_obj(self, obj: AbstractObject) -> WorldEntityType:
        """
        Returns the entity associated with the object.
        """
        return AbstractWorldEntity.create(obj)

    def get_entity_by_id(self, entity_id: str) -> AbstractWorldEntity:
        return self.entities[entity_id]

    def add_agent(self, agent: AbstractAgent):
        self.agents.append(agent)
        self.agents[-1].host_world_id = self.id
        self.agents[-1].launch()

    def add_object(self, obj: AbstractObject):
        self.objects.append(obj)
        self.objects[-1].host_world_id = self.id
        self.objects[-1].launch_websocket_thread()

    # TODO: delete objects and agents by id (stop thread, then remove from list)
    # TODO: update and restart objects and agents close threads and launch new ones
    # TODO: be able to stop the world and restart it

    def launch(self, host: str = "127.0.0.1", port: int = 7456):
        socket_server_start(host=host, port=port)
        sleep(0.2)
        self.launch_websocket_thread()
        sleep(0.2)
        for agent in self.agents:
            sleep(0.1)
            self.add_agent(agent)

        for obj in self.objects:
            sleep(0.1)
            self.add_object(obj)
