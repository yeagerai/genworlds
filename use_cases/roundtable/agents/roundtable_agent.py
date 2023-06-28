


from genworlds.agents.tree_agent.tree_agent import TreeAgent
from use_cases.roundtable.brains.event_filler_brain import EventFillerBrain
from use_cases.roundtable.brains.navigation_brain import NavigationBrain
from use_cases.roundtable.brains.podcast_brain import PodcastBrain


class RoundtableAgent(TreeAgent):

    def __init__(
        self,
        openai_api_key: str,
        id: str,
        name: str,
        role: str,
        background: str,
        goals: list[str],
        constraints: list[str],
        evaluation_principles: list[str],
    ):
        super().__init__(
            id=id,
            name=name,
            description=role,
            goals=goals,
            openai_api_key=openai_api_key,


            interesting_events={
                "agent_speaks_into_microphone",
                "agent_gives_object_to_agent_event",
            },
            wakeup_events={
                "agent_gives_object_to_agent_event": {
                    "recipient_agent_id": id,
                } 
            },

            navigation_brain = NavigationBrain(
                openai_api_key=openai_api_key,
                name=name, 
                role=role,
                background=background,
                constraints=constraints,
                evaluation_principles=evaluation_principles,
                n_of_thoughts=3,
            ),
            execution_brains={
                "podcast_brain": PodcastBrain(
                    openai_api_key=openai_api_key,
                    name=name, 
                    role=role,
                    background=background,
                    constraints=constraints,
                    evaluation_principles=evaluation_principles,
                    n_of_thoughts=1,
                ),
                "event_filler_brain": EventFillerBrain(
                    openai_api_key=openai_api_key,
                    name=name, 
                    role=role,
                    background=background,
                    constraints=constraints,
                    evaluation_principles=evaluation_principles,
                    n_of_thoughts=3,
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