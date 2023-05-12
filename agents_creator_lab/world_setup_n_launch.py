import os
from dotenv import load_dotenv
import concurrent.futures
from yeager_core.simulation.simulation import Simulation
from yeager_core.properties.basic_properties import Coordinates, Size
from agents_creator_lab.objects.blackboard import Blackboard
from yeager_core.agents.yeager_autogpt.agent import YeagerAutoGPT
from yeager_core.worlds.world_2d.world_2d import World2D

thread_pool_ref = concurrent.futures.ThreadPoolExecutor

home_path = os.path.expanduser("~")
load_dotenv(dotenv_path=os.path.join(home_path, ".yeagerai-sessions/.env"))
openai_api_key = os.getenv("OPENAI_API_KEY")

blackboard = Blackboard(
    name="blackboard",
    description="The blackboard is a place where agents can read and write all the jobs they have to do while in the lab",
)

researcher = YeagerAutoGPT(
    ai_name="Timmy",
    description="You are a researcher in the lab. You have to do all the jobs that are in the blackboard.",
    goals=["Finish all the jobs that are in the blackboard"],
    openai_api_key=openai_api_key,
)

world = World2D(
    name="agents_creator_lab",
    description="This is a lab where agents can be created",
)

simulation = Simulation(
    name="agents_creator_lab",
    description="This is a lab where agents can be created",
    world=world,
    objects=[
        (blackboard, {"position": Coordinates(x=200, y=500), "size": Size(width=16, height=9)})
    ],
    agents=[(researcher, {"position": Coordinates(x=0, y=0), "size": Size(width=1, height=1)})],
)

# this attaches to the websocket all the objects and agents in the world
simulation.launch()
