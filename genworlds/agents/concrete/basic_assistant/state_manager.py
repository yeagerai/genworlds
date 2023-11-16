from time import sleep
from genworlds.agents.abstracts.state_manager import AbstractStateManager
from genworlds.agents.abstracts.agent_state import AbstractAgentState
from genworlds.agents.abstracts.agent import AbstractAgent

from genworlds.worlds.concrete.base.actions import AgentWantsUpdatedStateEvent
from genworlds.agents.memories.simulation_memory import SimulationMemory


class BasicAssistantStateManager(AbstractStateManager):
    """This state manager keeps track of the current state of the agent."""

    def __init__(
        self, host_agent: AbstractAgent, state: AbstractAgentState, openai_api_key: str
    ):
        self.host_agent = host_agent
        self.state = state
        if not state:
            self.state = self._initialize_state(host_agent)
        else:
            self.state = state

        self.memory = SimulationMemory(openai_api_key=openai_api_key)

    def _initialize_state(
        self,
    ) -> (
        AbstractAgentState
    ):  # should trigger an action to get the initial state from the world
        return AbstractAgentState(
            name=self.host_agent.name,
            id=self.host_agent.id,
            goals=[
                "Starts waiting and sleeps till the user starts a new question.",
                f"Once {self.host_agent.name} receives a user's question, he makes sure to have all the information before sending the answer to the user.",
                f"When {self.host_agent.name} has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.",
                "After sending the response, he waits for the next user question.",
                "If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.",
            ],
            available_entities={},
            available_action_schemas={},
            current_action_chain=[],
            host_world_prompt="",
            is_asleep=False,
            simulation_memory_persistent_path="./",
            important_event_types=set(),  # fill
            interesting_event_types=set(),  # fill
            wakeup_event_types=set(),  # fill
            action_schema_chains=[],
        )

    def get_updated_state(self) -> AbstractAgentState:
        self.host_agent.send_event(
            AgentWantsUpdatedStateEvent(
                sender_id=self.host_agent.id, target_id=self.host_agent.host_world_id
            )
        )
        # retrieve memory and update last_retrieved_memory
        query = "No plan" if self.state.plan == [] else str(self.state.plan)
        self.host_agent.state_manager.state.last_retrieved_memory = (
            self.memory.get_event_stream_memories(query=query)
        )
        # meanwhile the concrete.base world processes the request and triggers the basic_assistant actions that update the state
        return self.state
