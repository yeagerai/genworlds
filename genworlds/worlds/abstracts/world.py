from typing import Generic, TypeVar, List
from abc import abstractmethod
from time import sleep
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.worlds.abstracts.world_entity import AbstractWorldEntity

from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.events.abstracts.action import AbstractAction

WorldEntityType = TypeVar("WorldEntityType", bound=AbstractWorldEntity)

class AbstractWorld(Generic[WorldEntityType], AbstractObject):
    """
    An Abstract Base Class representing a generic world in the simulation.
    """

    @property
    @abstractmethod
    def get_available_entities(cls) -> AbstractAction:
        """
        An AbstractAction that, when called, should return the list of available entities in the world.
        So you can define what available means, maybe security criteria, or maybe just the list of all actions, 
        or by locations, etc.
        """
        pass

    @property
    @abstractmethod
    def get_available_action_schemas(cls) -> AbstractAction:
        """
        An AbstractAction that, when called, should return the list of available action schemas in the world.
        So you can define what available means, maybe security criteria, or maybe just the list of all actions, 
        or by locations, etc.
        """
        pass

    # @property
    # @abstractmethod
    # def stop_world(cls) -> AbstractAction:
    #     pass

    @property
    @abstractmethod
    def objects(self) -> List[AbstractObject]:
        """
        A list of objects in the world.
        """
        pass

    @property
    @abstractmethod
    def agents(self) -> List[AbstractAgent]:
        """
        A list of agents in the world.
        """
        pass

    def get_entity_from_obj(self, obj: AbstractObject) -> WorldEntityType:
        """
        Returns the entity associated with the object.
        """
        return AbstractWorldEntity.create(obj)

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

    def launch(self):
        # Register agents and objects with the world
        for agent in self.agents:
            agent.host_world_id = self.id

        for obj in self.objects:
            obj.host_world_id = self.id

        # Launch the world
        self.launch_websocket_thread()

        sleep(1)

        for agent in self.agents:
            sleep(0.1)
            agent.launch()

        for obj in self.objects:
            sleep(0.1)
            obj.launch_websocket_thread()