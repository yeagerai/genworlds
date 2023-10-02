from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from genworlds.agents.abstracts.thought import AbstractThought
from genworlds.agents.abstracts.agent_state import AbstractAgentState
from genworlds.events.abstracts.event import AbstractEvent


class AbstractActionPlanner(ABC):
    def __init__(
        self,
        action_schema_selector: AbstractThought,
        event_filler: AbstractThought,
        other_thoughts: List[
            AbstractThought
        ] = [],  # other trigger event param filler thoughts
    ):
        self.action_schema_selector = action_schema_selector
        self.event_filler = event_filler
        self.other_thoughts = other_thoughts

    def plan_next_action(self, state: AbstractAgentState) -> Tuple[str, AbstractEvent]:
        if len(state.current_action_chain) > 0:
            action_schema = state.current_action_chain.pop(0)
            trigger_event = self.fill_triggering_event(action_schema, state)
            return action_schema, trigger_event
        action_schema = self.select_next_action_schema(state)
        trigger_event = self.fill_triggering_event(action_schema, state)
        return action_schema, trigger_event

    @abstractmethod
    def select_next_action_schema(self, state: AbstractAgentState) -> str:
        """Select the next action schema based on the given state.

        :param state: The state based on which the next action schema should be selected.
        :return: The action schema, e.g., "MoveTo".
        """
        pass

    @abstractmethod
    def fill_triggering_event(
        self, next_action_schema: str, state: AbstractAgentState
    ) -> Dict[str, Any]:
        """Fill the triggering event parameters based on the given state.

        :param state: The state based on which the triggering event parameters should be filled.
        :return: The triggering event parameters, e.g., {"arg1": x, "arg2": y, ...}.
        """
        pass
