from typing import Type
import json
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.agents.abstracts.agent_state import AbstractAgentState
from genworlds.agents.abstracts.thought import AbstractThought
from langchain.chat_models import ChatOpenAI
from langchain.chains.openai_functions import (
    create_structured_output_chain,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


class EventFillerThought(AbstractThought):
    def __init__(
        self,
        agent_state: AbstractAgentState,
        openai_api_key: str,
        model_name: str = "gpt-3.5-turbo",
    ):
        self.agent_state = agent_state
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=self.model_name, openai_api_key=openai_api_key, temperature=0.1
        )

    def run(self, trigger_event_class: Type[AbstractEvent]):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are {agent_name}, {agent_description}."),
                (
                    "system",
                    "You are embedded in a simulated world with those properties {agent_world_state}",
                ),
                ("system", "Those are your goals: \n{goals}"),
                (
                    "system",
                    "And this is your current plan to achieve the goals: \n{plan}",
                ),
                (
                    "system",
                    "Here is your memories of all the events that you remember from being in this simulation: \n{memory}",
                ),
                (
                    "system",
                    "Those are the available entities that you can choose from: \n{available_entities}",
                ),
                (
                    "system",
                    "Here you have pre-filled parameters coming from your previous thoughts if any: \n{other_thoughts_filled_parameters}",
                ),
                (
                    "system",
                    "Here is the triggering event schema: \n{triggering_event_schema}",
                ),
                ("human", "{footer}"),
            ]
        )

        chain = create_structured_output_chain(
            output_schema=trigger_event_class.schema(),
            llm=self.llm,
            prompt=prompt,
            verbose=True,
        )
        response = chain.run(
            agent_name=self.agent_state.name,
            agent_description=self.agent_state.description,
            agent_world_state=self.agent_state.host_world_prompt,
            goals=self.agent_state.goals,
            plan=self.agent_state.plan,
            memory=self.agent_state.last_retrieved_memory,
            available_entities=self.agent_state.available_entities,
            other_thoughts_filled_parameters=self.agent_state.other_thoughts_filled_parameters,
            triggering_event_schema=json.dumps(trigger_event_class.schema()),
            footer="""Fill the parameters of the triggering event based on the previous context that you have about the world.
            """,
        )
        response = trigger_event_class.parse_obj(response)

        return response
