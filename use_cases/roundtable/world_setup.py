import importlib
import inspect
import os
import threading
from dotenv import load_dotenv
import concurrent.futures

from qdrant_client import QdrantClient

import yaml

from genworlds.agents.base_agent.brains.single_eval_brain import SingleEvalBrain
from genworlds.agents.base_agent.prompts.execution_generator_prompt import ExecutionGeneratorPrompt
from genworlds.agents.base_agent.prompts.navigation_generator_prompt import NavigationGeneratorPrompt

from genworlds.simulation.simulation import Simulation
from genworlds.agents.base_agent.base_agent import BaseAgent
from genworlds.worlds.world_2d.world_2d import World2D
from use_cases.roundtable.objects.microphone import Microphone

thread_pool_ref = concurrent.futures.ThreadPoolExecutor

load_dotenv(dotenv_path=".env")
openai_api_key = os.getenv("OPENAI_API_KEY")

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

personality_db_qdrant_client = None


def load_yaml(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as stream:
        yaml_data = yaml.safe_load(stream)

    return yaml_data


def load_class(class_path):
    module_path, class_name = class_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    class_ = getattr(module, class_name)
    return class_

def construct_object(object_data, base_kwargs):
    if not isinstance(object_data, dict):
        raise ValueError("Object must be a dictionary")

    # Extract class
    cls = load_class(object_data['class'])

    # Retrieve the argument names from the constructor
    arg_names = inspect.getfullargspec(cls.__init__).args

    # Filter the dictionary to only include keys that correspond to the class constructor's parameters
    filtered_data = {k: v for k, v in object_data.items() if k in arg_names}

    # Separate out world-specific properties
    world_properties = object_data.get('world_properties', {})

    # Create the object
    obj = cls(**base_kwargs, **filtered_data)

    return obj, world_properties

def construct_agent(agent_data, base_agent_data, base_kwargs):
    if not isinstance(agent_data, dict):
        raise ValueError("Agent data must be a dictionary")
    if not isinstance(base_agent_data, dict):
        raise ValueError("Base agent data must be a dictionary")
    
    # Add base agent data
    combined_agent_data = {}
    for k in set(agent_data) | set(base_agent_data):
        if k in agent_data and agent_data[k] != None and k in base_agent_data and base_agent_data[k] != None:
            combined_agent_data[k] = base_agent_data[k] + agent_data[k]
        elif k in agent_data and agent_data[k] != None:
            combined_agent_data[k] = agent_data[k]
        elif k in base_agent_data and base_agent_data[k] != None:
            combined_agent_data[k] = base_agent_data[k]

    # Extract class
    cls = load_class(combined_agent_data['class'])

    # Retrieve the argument names from the constructor
    arg_names = inspect.getfullargspec(cls.__init__).args

    # Filter the dictionary to only include keys that correspond to the class constructor's parameters
    filtered_agent_data = {k: v for k, v in combined_agent_data.items() if k in arg_names}    

    # Separate out world-specific properties
    world_properties = combined_agent_data.get('world_properties', {})

    # Create the agent
    agent = cls(
        openai_api_key=openai_api_key,
        **base_kwargs,
        **filtered_agent_data,
    )

    return agent, world_properties


def construct_world(data):
    if 'world' not in data:
        raise ValueError("Missing 'world' in data")
    
    base_kwargs = data.get('base_args', {})

    world_def = data['world']

    # Construct all objects
    objects = [construct_object(obj, base_kwargs) for obj in world_def.get('objects', [])]

    # Get the base agent data
    base_agent_data = world_def.get('base_agent', {})
    if 'path_to_external_memory' in world_def:
        personality_db_qdrant_client = QdrantClient(path=os.path.join(ABS_PATH, world_def['path_to_external_memory']))
        base_agent_data['personality_db_qdrant_client'] = personality_db_qdrant_client

    # Construct all agents
    agents = [construct_agent(agent, base_agent_data, base_kwargs) for agent in world_def.get('agents', [])]  # Assuming you have a construct_agent function

    # Extract class
    cls = load_class(world_def['class'])

    # Retrieve the argument names from the constructor
    arg_names = inspect.getfullargspec(cls.__init__).args
    print(arg_names)

    # Filter the dictionary to only include keys that correspond to the class constructor's parameters
    filtered_world_def = {k: v for k, v in world_def.items() if k in arg_names}

    # Construct the world object
    world = cls(**base_kwargs, **filtered_world_def)

    # Extract locations
    locations = world_def.get('locations', [])

    return world, objects, agents, locations

def merge_dicts(d1, d2):
    for key, value in d2.items():
        if isinstance(value, dict):
            # get node or create one
            node = d1.setdefault(key, {})
            merge_dicts(node, value)
        else:
            d1[key] = value

    return d1

def launch_use_case(world_definition="default_world_definition.yaml", stop_event: threading.Event = None, yaml_data_override={}):
    yaml_data = merge_dicts(load_yaml(os.path.join(ABS_PATH, "world_definitions", world_definition)), yaml_data_override)
    print(yaml_data)

    world, objects, agents, locations = construct_world(yaml_data['world_definition'])

    simulation = Simulation(
        name=world.name,
        description=world.description,
        world=world,
        objects=objects,
        agents=agents,
        stop_event=stop_event,
    )

    # this attaches to the websocket all the objects and agents in the world
    simulation.launch()

if __name__ == "__main__":
    launch_use_case()
