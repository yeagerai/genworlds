from genworlds.agents.base_agent.base_agent import BaseAgent
from genworlds.agents.base_agent.thoughts.navigation_thought import NavigationThought
from genworlds.agents.base_agent.thoughts.event_filler_thought import EventFillerThought


def generate_base_agent(role: str, agent_name: str, openai_api_key: str):
    """
    Method for generating super simple dummy agents.
    """
    name = agent_name
    role = role
    background = """"""
    personality = f"""{agent_name} is very diligent."""
    goals = [
        "Starts waiting and sleeps till the user starts a new question.",
        f"Once {agent_name} receives a user's question, he makes sure to have all the information before sending the answer to the user.",
        f"When {agent_name} has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.",
        "After sending the response, he waits for the next user question.",
        "If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.",
    ]
    constraints = []
    evaluation_principles = []
    topic_of_conversation = "Help the user."

    return BaseAgent(
        name=name,
        id=name,
        description=f"{role}. {background}",
        goals=goals,
        openai_api_key=openai_api_key,
        wakeup_events={
            "agent_speaks_with_agent_event": {"target_id": name},
            "user_speaks_with_agent_event": {"target_id": name},
        },
        important_event_types=(),
        navigation_thought=NavigationThought(
            openai_api_key=openai_api_key,
            name=name,
            role=role,
            background=background,
            personality=personality,
            topic_of_conversation=topic_of_conversation,
            constraints=constraints,
            evaluation_principles=evaluation_principles,
            n_of_thoughts=3,
        ),
        execution_thoughts={
            "event_filler_thought": EventFillerThought(
                openai_api_key=openai_api_key,
                name=name,
                role=role,
                background=background,
                topic_of_conversation=topic_of_conversation,
                constraints=constraints,
                evaluation_principles=evaluation_principles,
                n_of_thoughts=1,
            ),
        },
        action_thought_map={
            "default": {"thought_chain": ["event_filler_thought"], "next_actions": []},
        },
    )
