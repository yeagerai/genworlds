import os
from dotenv import load_dotenv

from yeager_core.worlds.base_world import BaseWorld
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.events.base_event import EventDict, EventHandler
from agents_creator_lab.objects.blackboard import Blackboard
from yeager_core.agents.yeager_autogpt.agent import YeagerAutoGPT

home_path = os.path.expanduser("~")
load_dotenv(dotenv_path=os.path.join(home_path, ".yeagerai-sessions/.env"))
openai_api_key = os.getenv("OPENAI_API_KEY")

blackboard = Blackboard(
    name="blackboard",
    description="The blackboard is a place where agents can read and write all the jobs they have to do while in the lab",
    position=Coordinates(x=200, y=500),
    size=Size(width=16, height=9),
    important_event_types=[],
    event_dict=EventDict(),
    event_handler=EventHandler(),
)

researcher = YeagerAutoGPT(
    ai_name="Timmy",
    description="You are a researcher in the lab. You have to do all the jobs that are in the blackboard.",
    goals=["Finish all the jobs that are in the blackboard"],
    position=Coordinates(x=0, y=0),
    size=Size(width=5, height=5),
    vision_radius=100,
    important_event_types=[],
    event_dict=EventDict(),
    event_handler=EventHandler(),
    openai_api_key=openai_api_key,
)

world = BaseWorld(
    name="agents_creator_lab",
    description="This is a lab where agents can be created",
    position=Coordinates(x=0, y=0),
    size=Size(width=1000, height=1000),
    important_event_types=[],
    event_dict=EventDict(),
    event_handler=EventHandler(),
    objects=[blackboard],
    agents=[researcher],
)

# this attaches to the websocket all the objects and agents in the world
world.launch()
