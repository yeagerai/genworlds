from __future__ import annotations
from typing import List, Type
from abc import ABC, abstractmethod
from genworlds.events.abstracts.action import AbstractAction
from genworlds.simulation.sockets.handlers.event_handler import SimulationSocketEventHandler


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
    def websocket_url(self) -> str:
        """
        Returns the websocket URL.
        The default is ws://127.0.0.1:7456/ws
        """
        pass

    @property
    @abstractmethod
    def actions(self) -> List[Type[AbstractAction]]:
        """Returns the list of actions associated with the object."""
        pass

    def register_actions(self):
        """
        Registers the actions associated with the object.
        """
        for action in self.actions:
            self.register_event_listener(event_class=action.trigger_event_class, event_listener=action)
