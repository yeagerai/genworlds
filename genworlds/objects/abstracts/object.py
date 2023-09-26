from typing import List, Type
from genworlds.simulation.sockets.handlers.event_handler import (
    SimulationSocketEventHandler,
)
from genworlds.events.abstracts.action import AbstractAction


class AbstractObject(SimulationSocketEventHandler):
    """
    A Class representing a generic object in the simulation.
    """

    def __init__(
        self,
        name: str,
        id: str,
        description: str,
        host_world_id: str = None,
        actions: List[Type[AbstractAction]] = [],
    ):
        self.host_world_id = host_world_id
        self.name = name
        self.description = description

        super().__init__(id=id, actions=actions)
