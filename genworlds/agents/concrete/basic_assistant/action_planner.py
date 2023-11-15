from typing import Dict, Any, List
import json
from datetime import datetime
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.agents.abstracts.action_planner import AbstractActionPlanner
from genworlds.agents.abstracts.agent_state import AbstractAgentState
from genworlds.agents.abstracts.thought import AbstractThought
from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.agents.concrete.basic_assistant.thoughts.action_schema_selector import (
    ActionSchemaSelectorThought,
)
from genworlds.agents.concrete.basic_assistant.thoughts.event_filler import (
    EventFillerThought,
)
from genworlds.agents.abstracts.thought_action import ThoughtAction
from genworlds.utils.schema_to_model import json_schema_to_pydantic_model


class BasicAssistantActionPlanner(AbstractActionPlanner):
    """This action planner selects the action schema with the highest priority and fills the event parameters with the highest priority."""

    def __init__(
        self,
        host_agent: AbstractAgent,
        openai_api_key,
        initial_agent_state: AbstractAgentState,
        other_thoughts: List[AbstractThought] = [],
        model_name: str = "gpt-3.5-turbo-1106",
    ):
        self.host_agent = host_agent
        action_schema_selector = ActionSchemaSelectorThought(
            openai_api_key=openai_api_key,
            agent_state=initial_agent_state,
            model_name=model_name,
        )
        event_filler = EventFillerThought(
            openai_api_key=openai_api_key,
            agent_state=initial_agent_state,
            model_name=model_name,
        )
        other_thoughts = other_thoughts
        super().__init__(
            action_schema_selector,
            event_filler,
            other_thoughts,
        )

    def select_next_action_schema(self, state: AbstractAgentState) -> str:
        # call action_schema_selector thought with the correct parameters
        (
            next_action_schema,
            updated_plan,
        ) = self.action_schema_selector.run()  # gives enum values
        state.plan = updated_plan
        if next_action_schema in [el[0] for el in state.action_schema_chains]:
            state.current_action_chain = state.action_schema_chains[
                [el[0] for el in state.action_schema_chains].index(next_action_schema)
            ][1:]
        return next_action_schema

    def fill_triggering_event(
        self, next_action_schema: str, state: AbstractAgentState
    ) -> Dict[str, Any]:
        # check if is a thought action and compute the missing parameters
        if next_action_schema.startswith(self.host_agent.id):
            next_action = [
                action
                for action in self.host_agent.actions
                if next_action_schema == action.action_schema[0]
            ][0]
            trigger_event_class = next_action.trigger_event_class
            if isinstance(next_action, ThoughtAction):
                for param in next_action.required_thoughts:
                    thought_class = next_action.required_thoughts[param]
                    thought = thought_class(self.host_agent.state_manager.state)
                    state.other_thoughts_filled_parameters[param] = thought.run()

        else:
            trigger_event_class_schema = json.loads(
                self.host_agent.state_manager.state.available_action_schemas[
                    next_action_schema
                ].split("|")[-1]
            )
            trigger_event_class = json_schema_to_pydantic_model(
                trigger_event_class_schema
            )

        trigger_event: AbstractEvent = self.event_filler.run(trigger_event_class)
        trigger_event.created_at = datetime.now().isoformat()
        return trigger_event
