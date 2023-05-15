import os
from dotenv import load_dotenv
import concurrent.futures
from agents_creator_lab.objects.microphone import Microphone
from yeager_core.simulation.simulation import Simulation
from yeager_core.properties.basic_properties import Coordinates, Size
from agents_creator_lab.objects.blackboard import Blackboard
from yeager_core.agents.yeager_autogpt.agent import YeagerAutoGPT
from yeager_core.worlds.world_2d.world_2d import World2D

thread_pool_ref = concurrent.futures.ThreadPoolExecutor

home_path = os.path.expanduser("~")
load_dotenv(dotenv_path=os.path.join(home_path, ".yeagerai-sessions/.env"))
openai_api_key = os.getenv("OPENAI_API_KEY")

# blackboard = Blackboard(
#     name="blackboard",
#     description="The blackboard is a place where agents can read and write all the jobs they have to do while in the lab",
# )

podcast_host = YeagerAutoGPT(
    id="chamath",
    ai_name="Chamath Palihapitiya",
    description="The host of the All-in podcast",
    goals=["Host an episode of the All-in podcast, discussing AI technology"],
    openai_api_key=openai_api_key,
)

podcast_guest = YeagerAutoGPT(
    id="jason",	
    ai_name="Jason Calacanis",
    description="A co-host of the All-in podcast",
    goals=["Participate an episode of the All-in podcast, discussing AI technology"],
    openai_api_key=openai_api_key,
)


microphone = Microphone(
    id="microphone",
    name="Microphone",
    description="A podcast microphone that allows the holder of it to speak to the audience",
    host=podcast_host.id
)



world = World2D(
    id="world",
    name="roundtable",
    description="This is a podcast studio, where you record the All-in podcast. There is a microphone, and only the holder of the microphone can speak to the audience",
    locations=["roundtable"],
)

simulation = Simulation(
    name="roundable",
    description="This is a podcast studio, where you record the All-in podcast. There is a microphone, and only the holder of the microphone can speak to the audience",
    world=world,
    objects=[
        (microphone, {"held_by": podcast_host.id}),
    ],
    agents=[
        (podcast_host, {"location": "roundtable"}),
        (podcast_guest, {"location": "roundtable"}),
    ],
)

# this attaches to the websocket all the objects and agents in the world
simulation.launch()
