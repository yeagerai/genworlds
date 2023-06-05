import os
from dotenv import load_dotenv
import concurrent.futures


from genworlds.simulation.simulation import Simulation
from genworlds.agents.tree_agent.agent import TreeAgent
from genworlds.worlds.world_2d.world_2d import World2D
from use_cases.roundtable.objects.microphone import Microphone

thread_pool_ref = concurrent.futures.ThreadPoolExecutor

load_dotenv(dotenv_path=".env")
openai_api_key = os.getenv("OPENAI_API_KEY")

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

podcast_host = TreeAgent(
    id="maria",
    ai_name="Maria",
    description="The host of the podcast",
    goals=[
        "Host an episode of the Roundtable podcast, discussing AI technology.",
        "Only the holder of the microphone can speak to the audience, if you don't have the microphone in your inventory, wait to receive it from the previous speaker.",
        "Don't repeat yourself, respond to questions and points made by other co-hosts to advance the conversation.",
        "Don't hog the microphone for a long time, make sure to give it to other participants.",        
    ],
    openai_api_key=openai_api_key,
    model_name="gpt-4",
    search_algorithm="BFS",
    interesting_events={
        "agent_speaks_into_microphone",
        "agent_gives_object_to_agent_event",
    },
)

podcast_guest = TreeAgent(
    id="jimmy",
    ai_name="Jimmy",
    description="A guest of the podcast",
    goals=[
        "Participate in an episode of the Roundtable podcast, discussing AI technology.",
        "Only the holder of the microphone can speak to the audience, if you don't have the microphone in your inventory, wait to receive it from the previous speaker.",
        "Don't repeat yourself, respond to questions and points made by other co-hosts to advance the conversation.",
        "Don't hog the microphone for a long time, make sure to give it to other participants.",        
    ],
    openai_api_key=openai_api_key,
    model_name="gpt-4",
    search_algorithm="BFS",
    interesting_events={
        "agent_speaks_into_microphone",
        "agent_gives_object_to_agent_event",
    },
)


microphone = Microphone(
    id="microphone",
    name="Microphone",
    description="A podcast microphone that allows the holder of it to speak to the audience. The speaker can choose to make a statement, ask a question, respond to a question, or make a joke.",
    host=podcast_host.id,
)


world = World2D(
    id="world",
    name="Roundtable",
    description="This is a podcast studio, where you record the Roundtable podcast. There is a microphone, and only the holder of the microphone can speak to the audience",
    locations=["roundtable"],
)

simulation = Simulation(
    name="Roundable",
    description="This is a podcast studio, where you record the Roundtable podcast. There is a microphone, and only the holder of the microphone can speak to the audience",
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
