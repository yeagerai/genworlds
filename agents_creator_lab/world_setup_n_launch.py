from yeager_core.worlds.base_world import BaseWorld
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.events.base_event import EventDict, EventHandler
from agents_creator_lab.objects.blackboard import Blackboard

blackboard = Blackboard(
    name="blackboard",
    description="The blackboard is a place where agents can read and write all the jobs they have to do while in the lab",
    position=Coordinates(x=20, y=20, z=0),
    size=Size(width=16, height=9, depth=0),
    important_event_types=[],
    event_dict=EventDict(),
    event_handler=EventHandler(),
)

world = BaseWorld(
    name="agents_creator_lab",
    description="This is a lab where agents can be created",
    position=Coordinates(x=0, y=0, z=0),
    size=Size(width=100, height=100, depth=0),
    important_event_types=[],
    event_dict=EventDict(),
    event_handler=EventHandler(),
    objects=[blackboard],
    agents=[],
)

# this attaches to the websocket all the objects and agents in the world
world.launch()
