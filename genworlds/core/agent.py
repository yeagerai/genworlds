from typing import List, Callable
import asyncio

from genworlds.core.types import AgentState, WorldState, Event
from genworlds.core.comms import event_mult
from genworlds.core.llm_calls import call_openai, call_ollama
from genworlds.core.entity import get_world_state_dict

def agent_updates_internal_state(agent_state: AgentState, event: Event):
    updated_state = agent_state
    if agent_state.custom_state_updaters:
        for updater in agent_state.custom_state_updaters:
            updated_state = updater(updated_state, event)

    updated_state.memories.append(event)
    return updated_state

def actions_names_docstrings(actions: List[Callable]):
    return [f"__{action.__name__}__ : {action.__doc__}\n" for action in actions.values()]

def actions_names_as_string(actions: List[Callable]):
    return ', '.join([f'__{action.__name__}__' for action in actions.values()])

def choose_action_prompt_generator(agent_state: AgentState):
    prompt = (
        "\n## General info:\n"
        f"- your name: {agent_state.name}\n"
        f"- your description: {agent_state.description}\n"
        "## General goals:\n"
        f"{agent_state.goals}\n"
        "## Your previous plan:\n"
        f"{agent_state.plan}\n"
        "## Last memories from oldest to recent\n"
        f"{agent_state.memories}\n"
        "## Available Actions:\n"
        f"{''.join(actions_names_docstrings(agent_state.actions))}"
        f"\nYou can only perform one of the following actions: {actions_names_as_string(agent_state.actions)}\n No other actions are possible. Which one do you choose?"
    )
    return prompt

async def agent_chooses_action_name(agent_state: AgentState):
    prompt = choose_action_prompt_generator(agent_state)

    if agent_state.llm_platform == "openai":
        return await call_openai(agent_state.model_name, prompt, r"__([a-zA-Z]+(_[a-zA-Z]+)*)__", None)
    elif agent_state.llm_platform == "ollama":
        return await call_ollama(agent_state.endpoint, agent_state.model_name, prompt, r"__([a-zA-Z]+(_[a-zA-Z]+)*)__", None)
    else:
        return None
    
def get_action_function_by_meta_name(internal_state: AgentState, action_name: str):
    return next((action for action in internal_state.actions.values() if action.__name__ == action_name), None)

async def agent(id: str):
    agent_chan = asyncio.Queue()
    event_mult.subscribe(agent_chan)
    while True:
        new_event:Event = await agent_chan.get()
        try:
            if new_event.target_id in [id, "*"]:
                world_state = WorldState(**get_world_state_dict())
                internal_agent_state = getattr(world_state, "agent_states").get(id)
                new_internal_state = agent_updates_internal_state(internal_agent_state, new_event)
                chosen_action_name = (await agent_chooses_action_name(new_internal_state)).replace("__", "")
                chosen_action = get_action_function_by_meta_name(new_internal_state, chosen_action_name)

                if chosen_action:
                    asyncio.create_task(chosen_action("agent", id, new_internal_state, new_event))
        except AttributeError:
            continue
