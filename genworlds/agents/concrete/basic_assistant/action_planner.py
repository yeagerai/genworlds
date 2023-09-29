from typing import Dict, Any, List
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

class BasicAssistantActionPlanner(AbstractActionPlanner):
    """This action planner selects the action schema with the highest priority and fills the event parameters with the highest priority."""

    def __init__(
        self,
        host_agent: AbstractAgent,
        openai_api_key,
        initial_agent_state: AbstractAgentState,
        other_thoughts: List[AbstractThought] = [],
    ):
        self.host_agent = host_agent
        action_schema_selector = ActionSchemaSelectorThought(
            openai_api_key=openai_api_key,
            name=initial_agent_state.name,
            description=initial_agent_state.description,
            # constraints=initial_agent_state.constraints,
            # evaluation_principles=initial_agent_state.evaluation_principles,
            n_of_thoughts=3,
        )
        event_filler = EventFillerThought(
            openai_api_key=openai_api_key,
            name=initial_agent_state.name,
            description=initial_agent_state.description,
            # constraints=initial_agent_state.constraints,
            # evaluation_principles=initial_agent_state.evaluation_principles,
            n_of_thoughts=1,
        )
        other_thoughts = other_thoughts
        super().__init__(
            action_schema_selector,
            event_filler,
            other_thoughts,
        )

    def select_next_action_schema(self, state: AbstractAgentState) -> str:
        # call action_schema_selector thought with the correct parameters
        next_action_schema, updated_plan = self.action_schema_selector.run(
            {
                "goals": state.goals,
                "memory": state.last_retrieved_memory,
                "plan": state.plan,
                "agent_world_state": state.host_world_prompt,
                "available_entities": state.available_entities,
                "available_action_schemas": state.available_action_schemas,
            }
        )
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
        if next_action_schema.startswith("self"):
            next_action = self.host_agent.actions[self.host_agent.actions.index(next_action_schema)]
            if isinstance(next_action, ThoughtAction):
                for param in next_action.required_thoughts:
                    thought, run_dict = next_action.required_thoughts[param]
                    state.other_thoughts_filled_parameters[param] = thought.run(run_dict)

        trigger_event = self.event_filler.run(
            {
                "goals": state.goals,
                "memory": state.last_retrieved_memory,
                "plan": state.plan,
                "agent_world_state": state.host_world_prompt,
                "next_action_schema": next_action_schema,
                "other_thoughts_filled_parameters": state.other_thoughts_filled_parameters,
            }
        )
        return trigger_event
