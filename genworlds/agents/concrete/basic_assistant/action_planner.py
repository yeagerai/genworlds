from typing import Dict, Any, Tuple
from genworlds.agents.abstracts.action_planner import AbstractActionPlanner
from genworlds.agents.abstracts.agent_state import AbstractAgentState
from genworlds.agents.concrete.basic_assistant.thoughts import ActionSchemaSelectorThought, EventFillerThought


class BasicAssistantActionPlanner(AbstractActionPlanner):
    """This action planner selects the action schema with the highest priority and fills the event parameters with the highest priority."""
    action_schema_selector: ActionSchemaSelectorThought
    event_filler: EventFillerThought

    def select_next_action_schema(self, state: AbstractAgentState) -> str:
        # call action_schema_selector thought with the correct parameters
        next_action_schema = self.action_schema_selector.think(state)
        if next_action_schema in [el[0] for el in state.action_schema_chains]:
            state.current_action_chain = state.action_schema_chains[[el[0] for el in state.action_schema_chains].index(next_action_schema)][1:]
        return next_action_schema
    def fill_triggering_event(self, next_action_schema: str, state: AbstractAgentState) -> Dict[str, Any]:
        # check if is thought action
        if type(next_action_schema) == "ThoughtAction":
            # call corresponding thoughts
            ""
        trigger_event = self.event_filler.think(next_action_schema, state) 
        return trigger_event