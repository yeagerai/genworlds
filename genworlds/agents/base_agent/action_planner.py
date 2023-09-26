from typing import Tuple, Dict, Any

from genworlds.agents.base_agent.thoughts.thought import Thought
from genworlds.agents.abstracts.action_planner import AbstractActionPlanner
from genworlds.agents.abstracts.agent_state import AbstractAgentState


class BaseActionPlanner(AbstractActionPlanner):
    def __init__(
        self,
        navigation_thought: Thought,
        execution_thoughts: dict[str, Thought],
        action_thought_map,
    ):
        self.navigation_thought = navigation_thought
        self.execution_thoughts = execution_thoughts
        self.action_thought_map = action_thought_map

    def plan_next_action(self, state: AbstractAgentState) -> Tuple[str, Dict[str, Any]]:
        pass

    def _select_action_schema():
        pass

    def _fill_next_action_args():
        pass
