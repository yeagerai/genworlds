from typing import List
from genworlds.agents.abstracts.agent_state import AbstractAgentState
from genworlds.agents.abstracts.thought import AbstractThought
from langchain.chat_models import ChatOpenAI
from enum import Enum
from pydantic import BaseModel, Field
from langchain.chains.openai_functions import (
    create_structured_output_chain,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class ActionSchemaSelectorThought(AbstractThought):
    def __init__(
        self,
        agent_state: AbstractAgentState,
        openai_api_key: str,
        model_name: str = "gpt-3.5-turbo-1106",
    ):
        self.agent_state = agent_state
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=self.model_name, openai_api_key=openai_api_key, temperature=0.1
        )

    def run(self):
        class PlanNextAction(BaseModel):
            """Plans for the next action to be executed by the agent."""

            action_name: str = Field(
                ...,
                description="Selects the action name of the next action to be executed from the list of available action names.",
            )
            is_action_valid: bool = Field(
                ..., description="Determines whether the next action is valid or not."
            )
            is_action_valid_reason: str = Field(
                ...,
                description="Then explains the rationale of whether it is valid or not valid action.",
            )
            new_plan: List[str] = Field(
                ..., description="The new plan to execute to achieve the goals."
            )

        action_schemas_full_string = "## Available Actions: \n\n"
        for (
            action_schema_key,
            action_schema_value,
        ) in self.agent_state.available_action_schemas.items():
            action_schemas_full_string += (
                "Action Name: "
                + action_schema_key
                + "\nAction Description: "
                + action_schema_value.split("|")[0]
                + "\n\n"
            )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are {agent_name}, {agent_description}.\n"),
                (
                    "system",
                    "You are embedded in a simulated world with those properties {agent_world_state}\n",
                ),
                ("system", "Those are your goals: \n{goals}\n"),
                (
                    "system",
                    "And this is the previous plan to achieve the goals: \n{plan}\n",
                ),
                (
                    "system",
                    "Here is your memories of all the events that you remember from being in this simulation: \n{memory}\n",
                ),
                (
                    "system",
                    "Those are the available actions that you can choose from: \n{available_actions}\n",
                ),
                ("human", "{footer}\n"),
            ]
        )

        chain = create_structured_output_chain(
            PlanNextAction.schema(), self.llm, prompt, verbose=True
        )

        response = chain.run(
            agent_name=self.agent_state.name,
            agent_description=self.agent_state.description,
            agent_world_state=self.agent_state.host_world_prompt,
            goals=self.agent_state.goals,
            plan=self.agent_state.plan,
            memory=self.agent_state.last_retrieved_memory,
            available_actions=action_schemas_full_string,
            footer="""Select the next action which must be a value of the available actions that you can choose from based on previous context.
Also select whether the action is valid or not, and if not, why.
And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
            """,
        )
        response = PlanNextAction.parse_obj(response)
        return response.action_name, response.new_plan
