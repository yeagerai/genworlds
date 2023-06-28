import importlib
import inspect
import os
from dotenv import load_dotenv
import concurrent.futures

from qdrant_client import QdrantClient

import yaml

from genworlds.agents.tree_agent.brains.single_eval_brain import SingleEvalBrain
from genworlds.agents.tree_agent.prompts.execution_generator_prompt import ExecutionGeneratorPrompt
from genworlds.agents.tree_agent.prompts.navigation_generator_prompt import NavigationGeneratorPrompt

from genworlds.simulation.simulation import Simulation
from genworlds.agents.tree_agent.tree_agent import TreeAgent
from genworlds.worlds.world_2d.world_2d import World2D
from use_cases.roundtable.objects.microphone import Microphone

thread_pool_ref = concurrent.futures.ThreadPoolExecutor

load_dotenv(dotenv_path=".env")
openai_api_key = os.getenv("OPENAI_API_KEY")

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

def load_yaml(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as stream:
        yaml_data = yaml.safe_load(stream)

    return yaml_data

def load_class(class_path):
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    class_ = getattr(module, class_name)
    return class_

def construct_object(data):
    if not isinstance(data, dict):
        raise ValueError("Object must be a dictionary")

    # Extract class
    klass = load_class(data['class'])

    # Retrieve the argument names from the constructor
    arg_names = inspect.getfullargspec(klass.__init__).args

    # Filter the dictionary to only include keys that correspond to the class constructor's parameters
    filtered_data = {k: v for k, v in data.items() if k in arg_names}

    # Separate out world-specific properties
    world_properties = data.get('world_properties', {})

    # Create the object
    obj = klass(**filtered_data)

    return obj, world_properties

def construct_agent(agent_data, base_agent_data, qdrant_client: QdrantClient = None):
    if not isinstance(agent_data, dict):
        raise ValueError("Object must be a dictionary")
    if not isinstance(base_agent_data, dict):
        raise ValueError("Object must be a dictionary")
    
    # Add base agent data
    combined_agent_data = {}
    for k in set(agent_data) | set(base_agent_data):
        if k in agent_data and agent_data[k] != None and k in base_agent_data and base_agent_data[k] != None:
            combined_agent_data[k] = base_agent_data[k] + agent_data[k]
        elif k in agent_data and agent_data[k] != None:
            combined_agent_data[k] = agent_data[k]
        elif k in base_agent_data and base_agent_data[k] != None:
            combined_agent_data[k] = base_agent_data[k]

    print(combined_agent_data)

    # Extract class
    klass = load_class(combined_agent_data['class'])

    # Retrieve the argument names from the constructor
    arg_names = inspect.getfullargspec(klass.__init__).args

    # Filter the dictionary to only include keys that correspond to the class constructor's parameters
    filtered_agent_data = {k: v for k, v in combined_agent_data.items() if k in arg_names}    

    # Separate out world-specific properties
    world_properties = combined_agent_data.get('world_properties', {})

    # Create the agent
    agent = klass(
        openai_api_key=openai_api_key,
        **filtered_agent_data
    )

    return agent, world_properties


def construct_world(data):
    if 'world' not in data:
        raise ValueError("Missing 'world' in data")

    world_def = data['world']

    # Extnal memories
    if 'pato_to_external_memory' in world_def and world_def['pato_to_external_memory'] != None:
        pato_to_external_memory = world_def['pato_to_external_memory']
        personality_db_qdrant_client = QdrantClient(path=os.path.join(ABS_PATH, path_to_external_memory))

    # Construct all objects
    objects = [construct_object(obj) for obj in world_def.get('objects', [])]

    # Get the base agent data
    base_agent_data = world_def.get('base_agent', {})

    # Construct all agents
    agents = [construct_agent(agent, base_agent_data, personality_db_qdrant_client) for agent in world_def.get('agents', [])]  # Assuming you have a construct_agent function

    # Extract class
    klass = load_class(world_def['class'])

    # Retrieve the argument names from the constructor
    arg_names = inspect.getfullargspec(klass.__init__).args

    # Filter the dictionary to only include keys that correspond to the class constructor's parameters
    filtered_world_def = {k: v for k, v in world_def.items() if k in arg_names}

    # Construct the world object
    world = klass(**filtered_world_def)

    # Extract locations
    locations = world_def.get('locations', [])

    return world, objects, agents, locations


yaml_data = load_yaml(os.path.join(ABS_PATH, "world_definition.yaml"))

world, objects, agents, locations = construct_world(yaml_data['world_definition'])

simulation = Simulation(
    name=world.name,
    description=world.description,
    world=world,
    objects=objects,
    agents=agents,
)


# this attaches to the websocket all the objects and agents in the world
simulation.launch()
