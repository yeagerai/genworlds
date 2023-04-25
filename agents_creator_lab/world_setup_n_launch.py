from yeager_core.worlds.base_world import BaseWorld
from yeager_core.properties.basic_properties import Coordinates, Size

from .objects.blackboard import Blackboard

blackboard = Blackboard(
    name="blackboard",
    description="The blackboard is a place where agents can read and write all the jobs they have to do while in the lab",
    content=[],
)

world = BaseWorld(
    name="agents_creator_lab",
    description="This is a lab where agents can be created",
    position= Coordinates(x=0,y=0,z=0),
    size=Size(width=100, height=100, depth=100),
    important_event_types=[],
    objects=[blackboard],
    agents=[],
)

# this attaches to the websocket all the objects and agents in the world
world.launch() 