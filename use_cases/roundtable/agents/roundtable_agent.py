


from qdrant_client import QdrantClient
from genworlds.agents.base_agent.base_agent import BaseAgent
from use_cases.roundtable.brains.event_filler_brain import EventFillerBrain
from use_cases.roundtable.brains.navigation_brain import NavigationBrain
from use_cases.roundtable.brains.podcast_brain import PodcastBrain


class RoundtableAgent(BaseAgent):

    def __init__(
        self,
        openai_api_key: str,
        id: str,
        name: str,
        role: str,
        background: str,
        personality: str,
        communication_style: str,
        topic_of_conversation: str,
        goals: list[str],
        constraints: list[str],
        evaluation_principles: list[str],
        personality_db_qdrant_client: QdrantClient = None,
        personality_db_collection_name: str = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        super().__init__(
            id=id,
            name=name,
            description=f"{role}. {background}",
            goals=goals,
            openai_api_key=openai_api_key,
            websocket_url=websocket_url,
            personality_db_qdrant_client=personality_db_qdrant_client,
            personality_db_collection_name=personality_db_collection_name,

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
                personality=personality,
                topic_of_conversation=topic_of_conversation,
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
                    personality=personality,
                    communication_style=communication_style,
                    topic_of_conversation=topic_of_conversation,
                    constraints=constraints,
                    evaluation_principles=evaluation_principles,
                    n_of_thoughts=1,
                ),
                "event_filler_brain": EventFillerBrain(
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
            action_brain_map={
                "Microphone:agent_speaks_into_microphone": {"brains":[
                    "podcast_brain",
                    "event_filler_brain",
                ], "next_actions": ["World:agent_gives_object_to_agent_event"]},
                "World:agent_gives_object_to_agent_event": {"brains":["event_filler_brain"], "next_actions": []},
                "default": {"brains":["event_filler_brain"], "next_actions": []},
            },
        )