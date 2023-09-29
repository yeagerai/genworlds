from typing import List, Optional
from genworlds.agents.abstracts.thought import AbstractThought
from genworlds.events.abstracts.action import AbstractAction
from genworlds.agents.concrete.basic_assistant.agent import BasicAssistant
from genworlds.agents.abstracts.agent_state import AbstractAgentState


def generate_basic_assistant(
    openai_api_key: str,
    agent_name: str,
    description: str,
    host_world_id: Optional[str] = None,
    other_thoughts: List[AbstractThought] = [],
    action_classes: List[type[AbstractAction]] = [],
    action_schema_chains: List[List[str]] = [],
    simulation_memory_persistent_path: str = "./",
):
    """
    Method for generating super simple dummy agents.
    """

    # Static initialized in the constructor

    initial_agent_state = AbstractAgentState(
        name=agent_name,
        id=agent_name,
        description=description,
        goals=[
            "Starts waiting and sleeps till the user starts a new question.",
            f"Once {agent_name} receives a user's question, he makes sure to have all the information before sending the answer to the user.",
            f"When {agent_name} has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.",
            "After sending the response, he waits for the next user question.",
            "If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.",
        ],
        plan=[],
        last_retrieved_memory="",
        other_thoughts_filled_parameters = {},
        available_entities=[],
        available_action_schemas={},
        current_action_chain=[],
        host_world_prompt="",
        simulation_memory_persistent_path=simulation_memory_persistent_path,
        important_event_types=set(),  # fill
        interesting_event_types=set(),  # fill
        wakeup_event_types=set(),  # fill
        is_asleep=False,
        action_schema_chains=action_schema_chains,
    )

    return BasicAssistant(
        openai_api_key=openai_api_key,
        name=agent_name,
        id=agent_name,
        description=description,
        host_world_id=host_world_id,
        initial_agent_state=initial_agent_state,
        action_classes=action_classes,
        other_thoughts=other_thoughts,
    )
