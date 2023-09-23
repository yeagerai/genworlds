from __future__ import annotations
from typing import List, Type
from abc import ABC, abstractmethod
from genworlds.simulation.sockets.handlers.event_handler import SimulationSocketEventHandler
from genworlds.events.abstracts.action import AbstractAction


class AbstractObject(ABC, SimulationSocketEventHandler):
    """
    An Abstract Base Class representing a generic object in the simulation.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the object."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Returns the description of the object."""
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        """Returns the unique identifier of the object."""
        pass

    @property
    @abstractmethod
    def host_world_id(self) -> str:
        """Returns the id of the world hosting the object."""
        pass

    @property
    @abstractmethod
    def actions(self) -> List[Type[AbstractAction]]:
        """Returns the list of actions associated with the object."""
        pass
