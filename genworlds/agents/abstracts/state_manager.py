from abc import ABC, abstractmethod
from genworlds.agents.abstracts.agent_state import AbstractAgentState


class AbstractStateManager(ABC):
    state: AbstractAgentState

    @abstractmethod
    def get_updated_state(self) -> AbstractAgentState:
        """Retrieve the updated state"""
        pass
