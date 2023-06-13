import os
from dotenv import load_dotenv
import concurrent.futures
from genworlds.agents.tree_agent.brains.single_eval_brain import SingleEvalBrain
from genworlds.agents.tree_agent.prompts.execution_generator_prompt import ExecutionGeneratorPrompt
from genworlds.agents.tree_agent.prompts.navigation_generator_prompt import NavigationGeneratorPrompt


from genworlds.simulation.simulation import Simulation
from genworlds.agents.tree_agent.agent import TreeAgent
from genworlds.worlds.world_2d.world_2d import World2D
from use_cases.roundtable.objects.microphone import Microphone

thread_pool_ref = concurrent.futures.ThreadPoolExecutor

load_dotenv(dotenv_path=".env")
openai_api_key = os.getenv("OPENAI_API_KEY")

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

def navigation_brain_factory(name, background):
    return SingleEvalBrain(
        openai_api_key=openai_api_key,
        prompt_template_class=NavigationGeneratorPrompt,
        llm_params=[
            "plan",
            "goals",
            "memory",
            "personality_db",
            "agent_world_state",
            "nearby_entities",
            "inventory",
            "relevant_commands",
            "messages",
        ],
        n_of_thoughts=3,
        generator_role_prompt=f"You are {name}, {background}. You need to come up with the next step to get you closer to your goals. It must be consistent with all of the following information:",
        generator_results_prompt="""
# Response type
Look at your previous plan, your memories about what you have done recently and your goals, and propose {num_thoughts} possible plans that advance your goals.
Check if you have already completed a step in your plan, and if so, propose the next step as the first one.
Then, select the next action that you want to do to achieve the first step of your plan.
Check that the action is in the list of available actions, and that you meet all the preconditions for the action.
Use the following format and output {num_thoughts} lines of text AND NOTHING ELSE:
- {{ "step_completed": "If you completed a step of your plan, put it here, as well as an explanation of how you did it", "plan": "A numbered list of an updated plan", "goal": "Here is what I want to achieve in my next step using the next_action I select",  "next_action": "EntityClass:action_type_1", "is_action_valid": "Assess whether the action is valid based on the current state of the world."}}
- {{ "step_completed": "If you completed a step of your plan, put it here, as well as an explanation of how you did it", "plan": "A numbered list of an alternative updated plan", "goal": "Here is what I want to achieve in my next step using the next_action I select", "next_action": "EntityClass:action_type_1", "is_action_valid": "Assess whether the action is valid based on the current state of the world."}}
- {{ "step_completed": "If you completed a step of your plan, put it here, as well as an explanation of how you did it", "plan": "A numbered list of a third updated plan", , "goal": "Here is what I want to achieve in my next step using the next_action I select", "next_action": "EntityClass:action_type_2", "is_action_valid": "Assess whether the action is valid based on the current state of the world."}}
                """,
        evaluator_role_prompt=f"You are {name}, {background}. You are trying to evaluate a number of actions to see which will get you closer to your goals. It must be consistent with the following information:",
        evaluator_results_prompt="""
## Choose the Best Action
From the following options, pick the best plan and next action
Check that the proposed action is in the list of available actions, and that you meet all the preconditions for the action, like having the correct items in your inventory.
Here are the plans to choose from:
{thought_to_evaluate}

# Response type
Return the best plan of the options, and NOTHING ELSE:
            """,
        verbose=True,
    )

def podcast_brain_factory(name, background):
    return SingleEvalBrain(
        openai_api_key=openai_api_key,
        prompt_template_class=ExecutionGeneratorPrompt,
        llm_params=[
            # "plan",
            "goals",
            "memory",
            "personality_db",
            "agent_world_state",
            "nearby_entities",
            # "inventory",
            "command_to_execute",
            "previous_brain_outputs",
        ],
        n_of_thoughts=1,
        generator_role_prompt=f"You are {name}, {background}. You have to generate a podcast response based on:",
        generator_results_prompt="""
# Response type
Output {num_thoughts} possible paragraphs of text that would be a good next line for your to say in line with the goal you set for yourself, which moves the conversation forward and matches stylistically something you would say AND NOTHING ELSE.               
Do not narrate any actions you might take, only generate a piece of text.
Use the following format:
- The first possible paragraph
- A second possible paragraph
                """,
        evaluator_role_prompt=f"You are {name}, {background}. You are trying to evaluate a number possible things to next on the podcast. It must be consistent with the following information:",
        evaluator_results_prompt="""
## Outputs to evaluate
Evaluate the following paragraphs of text and choose the best one to say next.
{thought_to_evaluate}

# Response type
Output the best paragraph, and NOTHING ELSE:      
                """,
        verbose=True,
    )

def event_filler_brain_factory(name, background):
    return SingleEvalBrain(
        openai_api_key=openai_api_key,
        prompt_template_class=ExecutionGeneratorPrompt,
        llm_params=[
            "plan",
            "goals",
            "memory",
            "personality_db",
            "agent_world_state",
            "nearby_entities",
            "inventory",
            "command_to_execute",
            "previous_brain_outputs",
        ],
        n_of_thoughts=1,
        generator_role_prompt=f"""You are {name}, {background}. In previous steps, you have selected an action to execute, and possibly generated some of the response parameters - make sure to include those exactly. 
You now need to generate a valid set of JSON parameters for the command to execute, based on the following information:
                """,
        generator_results_prompt="""
# Response type
{num_thoughts} lines of json containing possible options for completing the arguments of the command to execute, each one with the following format AND NOTHING ELSE:
- {{"arg name": "value1", "arg name 2": "value2", ...}}
- {{"arg name": "alt value1", "arg name 2": "alt value2", ...}} 
            """,
        evaluator_role_prompt=f"You are {name}, {background}. ou need to evaluate the provided set of JSON parameters based on their correctness, with respect to all of the following information:",
        evaluator_results_prompt="""
## Parameters to evaluate
Evaluate the following list of possible parameter set in terms of their correctness:
{thought_to_evaluate}

# Response type
Return the best parameter set and NOTHING ELSE:      
            """,
        verbose=True,
    )




podcast_host = TreeAgent(
    id="maria",
    ai_name="Maria Podcastonova",
    description="The host of the Rountable podcast",
    goals=[
        "Host an episode of the Roundtable podcast, discussing AI technology.",
        "Only the holder of the microphone can speak to the audience, if you don't have the microphone in your inventory, wait to receive it from the previous speaker.",
        "Don't repeat yourself, ask insightful questions to the guests of the podcast to advance the conversation.",
        "If you have asked a question, make sure to give the microphone to the guest so they can answer.",
        "Don't hog the microphone for a long time, make sure to give it to other participants.",
        "If you have completed your statement, make sure to pass the microphone to the next speaker.",
    ],
    openai_api_key=openai_api_key,
    interesting_events={
        "agent_speaks_into_microphone",
        "agent_gives_object_to_agent_event",
    },
    wakeup_events={
        "agent_gives_object_to_agent_event": {} 
    },

    navigation_brain=navigation_brain_factory("Maria Podcastonova", "an expert podcaster and the host of the Rountable podcast"),
    execution_brains={
        "podcast_brain": podcast_brain_factory("Maria Podcastonova", "an expert podcaster and the host of the Rountable podcast"),
        "event_filler_brain": event_filler_brain_factory("Maria Podcastonova", "an expert podcaster and the host of the Rountable podcast"),
    },
    action_brain_map={
        "Microphone:agent_speaks_into_microphone": [
            "podcast_brain",
            "event_filler_brain",
        ],
        "World:agent_gives_object_to_agent_event": ["event_filler_brain"],
        "default": ["event_filler_brain"],
    },
)

podcast_guest = TreeAgent(
    id="jimmy",
    ai_name="Jimmy Artificles",
    description="A guest of the podcast, a world-renowned AI researcher.",
    goals=[
        "Participate in an episode of the Roundtable podcast, discussing AI technology.",
        "Only the holder of the microphone can speak to the audience, if you don't have the microphone in your inventory, wait to receive it from the previous speaker.",
        "Don't repeat yourself, respond to questions and points made by the host to advance the conversation.",
        "If you have asked a question, or have finished speaking, pass the microphone back to the host.",
        "Don't hog the microphone for a long time, make sure to give it to other participants.",
        "If you have completed your statement, make sure to pass the microphone to the next speaker.",
    ],
    openai_api_key=openai_api_key,
    interesting_events={
        "agent_speaks_into_microphone",
        "agent_gives_object_to_agent_event",
    },
    wakeup_events={
        "agent_gives_object_to_agent_event": {} 
    },

    navigation_brain=navigation_brain_factory("Jimmy Artificles", "a world-renowned AI researcher and a guest of the Rountable podcast"),
    execution_brains={
        "podcast_brain": podcast_brain_factory("Jimmy Artificles", "a world-renowned AI researcher and a guest of the Rountable podcast"),
        "event_filler_brain": event_filler_brain_factory("Jimmy Artificles", "a world-renowned AI researcher and a guest of the Rountable podcast"),
    },
    action_brain_map={
        "Microphone:agent_speaks_into_microphone": [
            "podcast_brain",
            "event_filler_brain",
        ],
        "World:agent_gives_object_to_agent_event": ["event_filler_brain"],
        "default": ["event_filler_brain"],
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
