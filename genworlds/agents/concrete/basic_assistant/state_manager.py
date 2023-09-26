from time import sleep
from genworlds.agents.abstracts.state_manager import AbstractStateManager
from genworlds.agents.abstracts.agent_state import AbstractAgentState
from genworlds.agents.abstracts.agent import AbstractAgent

from genworlds.worlds.concrete.base.actions import (
    AgentWantsUpdatedStateEvent
)

class BasicAssistantStateManager(AbstractStateManager):
    """This state manager keeps track of the current state of the agent."""
    
    def __init__(self, host_agent:AbstractAgent, state: AbstractAgentState):
        self.host_agent = host_agent
        self.state = state
        if not state:
            self.state = self._initialize_state(host_agent)
        else:
            self.state = state

    def _initialize_state(self) -> AbstractAgentState:
        return AbstractAgentState(
            id=self.host_agent.id, 
            available_entities={}, 
            available_action_schemas={},
            current_action_chain=[]
        )

    def get_updated_state(self) -> AbstractAgentState:
        self.host_agent.send_event(AgentWantsUpdatedStateEvent(sender_id=self.host_agent.id, target_id=self.host_agent.host_world_id))
        sleep(0.5) # meanwhile the concrete.base world processes the request and triggers the basic_assistant actions that update the state
        return self.state
