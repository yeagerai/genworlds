import os
from dotenv import load_dotenv
import concurrent.futures
from genworlds.agents.tree_agent.brains.event_filler_brain import EventFillerBrain
from genworlds.agents.tree_agent.brains.navigation_brain import NavigationBrain
from genworlds.agents.tree_agent.brains.podcast_brain import PodcastBrain


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
    ai_name="Maria Podcastonova",
    description="The host of the Rountable podcast",
    goals=[
        "Host an episode of the Roundtable podcast, discussing AI technology.",
        "Only the holder of the microphone can speak to the audience, if you don't have the microphone in your inventory, wait to receive it from the previous speaker.",
        "Don't repeat yourself, ask insightful questions to the guests of the podcast to advance the conversation.",
        "Don't hog the microphone for a long time, make sure to give it to other participants.",
    ],
    openai_api_key=openai_api_key,
    interesting_events={
        "agent_speaks_into_microphone",
        "agent_gives_object_to_agent_event",
    },

    navigation_brain=NavigationBrain(
        openai_api_key=openai_api_key,
        n_of_thoughts=3,
        generator_role_prompt="You are Maria. You need to choose your next action that helps you achieve your goals. It must be consistent with all of the following information:",
        generator_results_prompt="""# Response type
                A bullet list containing {num_thoughts} of possible plans and next events that help you achieve your large scale goals. You can use the same event multiple times with different goals in mind. If none of the actions make sense, you can also use the action "Self:wait". Use the following format:
                - {{ "plan": "1. plan step 1 2. plan step 2 3. plan step 3", "next_action": "Class:event_type_1", "goal": "I want to use this event to achieve a goal"}}
                - {{ "plan": "1. plan step 1 2. plan step 2 3. plan step 3", "next_action": "Class:event_type_1", "goal": "I want to use this event to achieve a different goal"}}
                - {{ "plan": "1. plan step 1 2. plan step 2 3. plan step 3"", "next_action": "Class:event_type_2", "goal": "I want to use this event to achieve a third goal"}}
            """,
        evaluator_role_prompt="You are Maria, an expert in evaluating which events get you closer to achieving your goals based on:",
        evaluator_results_prompt="""## Action to evaluate
                Evaluate the following plan by rating it from 0 to 1, where 0 means that the plan is not useful or possible, and 1 means that the plan is the best next step you can take:
                {thought_to_evaluate}

                # Response type
                Return the evaluation of the plan as a float between 0 and 1, and NOTHING ELSE:
            """,
            verbose=True,
    ),
    execution_brains={
        "podcast_brain": PodcastBrain(
            openai_api_key,
            n_of_thoughts=1,
            generator_role_prompt="You are Maria, an expert podcaster and the host of the Rountable podcast. You have to generate a podcast response based on:",
            generator_results_prompt="""# Response type
                Output {num_thoughts} possible paragraphs of text that would be a good next line for your to say in line with the goal you set for yourself, which moves the conversation forward and matches stylistically something you would say AND NOTHING ELSE.               
                Do not narrate any actions you might take, only generate a piece of text.
                Use the following format:
                - The first possible paragraph
                - A second possible paragraph
            """,
            evaluator_role_prompt="You are Maria, an expert in evaluating the quality and the depth of a podcast response based on:",
            evaluator_results_prompt="""## Thought to evaluate
                Evaluate the following thought by rating it from 0 to 1, where 0 means that the thought is not useful at all, and 1 means that the thought is very useful:
                {thought_to_evaluate}

                # Response type
                Return the evaluation of the thought as a float between 0 and 1, and NOTHING ELSE:      
            """,
            verbose=True,
        ),
        "event_filler_brain": EventFillerBrain(
            openai_api_key,
            n_of_thoughts=1,
            generator_role_prompt="""You are Maria, an expert podcaster and the host of the Rountable podcast. In previous steps, you have selected an action to execute, and possibly generated some of the response parameters in a previous step - make sure to include those exactly. 
                You now need to generate a valid set of JSON parameters for the command to execute, based on the following information:
            """,
            generator_results_prompt="""# Response type
                {num_thoughts} lines of json containing possible options for completing the arguments of the command to execute, each one with the following format AND NOTHING ELSE:
                - {{"arg name": "value1", "arg name 2": "value2", ...}}
                - {{"arg name": "alt value1", "arg name 2": "alt value2", ...}} 
            """,
            evaluator_role_prompt="You are Maria, an expert podcaster and the host of the Rountable podcast. You need to evaluate the provided set of JSON parameters based on their correctness, with respect to all of the following information:",
            evaluator_results_prompt="""## Parameters to evaluate
                Evaluate the following set of parameters by rating them from 0 to 1, where 0 means that the parameters are not correct, and 1 means that the parameters completely correct:
                {thought_to_evaluate}

                # Response type
                Return the evaluation of the parameters as a float between 0 and 1, and NOTHING ELSE:      
            """,
            verbose=True,
        ),
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
        "Don't hog the microphone for a long time, make sure to give it to other participants.",
    ],
    openai_api_key=openai_api_key,
    interesting_events={
        "agent_speaks_into_microphone",
        "agent_gives_object_to_agent_event",
    },

    navigation_brain=NavigationBrain(
        openai_api_key=openai_api_key,
        n_of_thoughts=3,
        generator_role_prompt="You are Jimmy, a world-renowned AI researcher and a guest of the Rountable podcast. You need to choose your next action that helps you achieve your goals. It must be consistent with all of the following information:",
        generator_results_prompt="""# Response type
                A bullet list containing {num_thoughts} of possible plans and next events that help you achieve your large scale goals. You can use the same event multiple times with different goals in mind. If none of the actions make sense, you can also use the action "Self:wait". Use the following format:
                - {{ "plan": "1. plan step 1 2. plan step 2 3. plan step 3", "next_action": "Class:event_type_1", "goal": "I want to use this event to achieve a goal"}}
                - {{ "plan": "1. plan step 1 2. plan step 2 3. plan step 3", "next_action": "Class:event_type_1", "goal": "I want to use this event to achieve a different goal"}}
                - {{ "plan": "1. plan step 1 2. plan step 2 3. plan step 3"", "next_action": "Class:event_type_2", "goal": "I want to use this event to achieve a third goal"}}
            """,
        evaluator_role_prompt="You are Jimmy, a world-renowned AI researcher and a guest of the Rountable podcast, an expert in evaluating which events get you closer to achieving your goals based on:",
        evaluator_results_prompt="""## Action to evaluate
                Evaluate the following plan by rating it from 0 to 1, where 0 means that the plan is not useful or possible, and 1 means that the plan is the best next step you can take:
                {thought_to_evaluate}

                # Response type
                Return the evaluation of the plan as a float between 0 and 1, and NOTHING ELSE:
            """,
        verbose=True,
    ),
    execution_brains={
        "podcast_brain": PodcastBrain(
            openai_api_key,
            n_of_thoughts=1,
            generator_role_prompt="You are Jimmy, a world-renowned AI researcher and a guest of the Rountable podcast. You have to generate a podcast response based on:",
            generator_results_prompt="""# Response type
                Output {num_thoughts} possible paragraphs of text that would be a good next line for your to say in line with the goal you set for yourself, which moves the conversation forward and matches stylistically something you would say AND NOTHING ELSE.                
                Do not narrate any actions you might take, only generate a piece of text.
                Use the following format:
                - The first possible paragraph
                - A second possible paragraph
            """,
            evaluator_role_prompt="You are Jimmy, a world-renowned AI researcher and a guest of the Rountable podcast, an expert in evaluating the quality and the depth of a podcast response based on:",
            evaluator_results_prompt="""## Thought to evaluate
                Evaluate the following thought by rating it from 0 to 1, where 0 means that the thought is not useful at all, and 1 means that the thought is very useful:
                {thought_to_evaluate}

                # Response type
                Return the evaluation of the thought as a float between 0 and 1, and NOTHING ELSE:      
            """,
            verbose=True,
        ),
        "event_filler_brain": EventFillerBrain(
            openai_api_key,
            n_of_thoughts=1,
            generator_role_prompt="""You are Jimmy, a world-renowned AI researcher and a guest of the Rountable podcast. In previous steps, you have selected an action to execute, and possibly generated some of the response parameters in a previous step - make sure to include those exactly. 
                You now need to generate a valid set of JSON parameters for the command to execute, based on the following information:
            """,
            generator_results_prompt="""# Response type
                {num_thoughts} lines of json containing possible options for completing the arguments of the command to execute, each one with the following format AND NOTHING ELSE:
                - {{"arg name": "value1", "arg name 2": "value2", ...}}
                - {{"arg name": "alt value1", "arg name 2": "alt value2", ...}} 
            """,
            evaluator_role_prompt="You are Jimmy, a world-renowned AI researcher and a guest of the Rountable podcast. You need to evaluate the provided set of JSON parameters based on their correctness, with respect to all of the following information:",
            evaluator_results_prompt="""## Parameters to evaluate
                Evaluate the following set of parameters by rating them from 0 to 1, where 0 means that the parameters are not correct, and 1 means that the parameters completely correct:
                {thought_to_evaluate}

                # Response type
                Return the evaluation of the parameters as a float between 0 and 1, and NOTHING ELSE:      
            """,
            verbose=True,
        ),
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
