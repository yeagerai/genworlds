from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from genworlds.agents.abstracts.thought import AbstractThought
from genworlds.agents.abstracts.agent_state import AbstractAgentState

class AbstractActionPlanner(ABC):

    @property
    @abstractmethod
    def action_schema_selector(self) -> AbstractThought:
        """Returns the thought that will be used to select the next action schema"""
        pass

    @property
    @abstractmethod
    def event_fillers(self) -> List[AbstractThought]:
        """Returns the event filler thoughts that will be used to fill the event parameters of the next action trigger event"""
        pass

    @abstractmethod
    def plan_next_action(self, state: AbstractAgentState) -> Tuple[str, Dict[str, Any]]:
        """Plan the next action based on the given state.
        
        This method should first call the action schema selector to get the action schema.
        Then it should call the event fillers to get the event parameters.
        
        :param state: The state based on which the next action should be planned.
        :return: A tuple containing the action schema and the trigger event parameters, e.g., {"arg1": x, "arg2": y, ...}.
        """
        pass