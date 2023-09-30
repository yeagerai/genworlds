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

    def __init__(self, agent_state: AbstractAgentState, openai_api_key: str, model_name: str = "gpt-4"):
        self.agent_state = agent_state
        self.model_name = model_name
        self.llm = ChatOpenAI(model=self.model_name, openai_api_key=openai_api_key, temperature=0.1)

    def run(self, trigger_event_class: AbstractEvent):


        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are {agent_name}, {agent_description}."),
                ("system", "You are embedded in a simulated world with those properties {agent_world_state}"),
                ("system", "Those are your goals: \n{goals}"),
                ("system", "And this is your current plan to achieve the goals: \n{plan}"),
                ("system", "Here is your memories of all the events that you remember from being in this simulation: \n{memory}"),
                ("system", "Here you have pre-filled parameters coming from your previous thoughts if any: \n{other_thoughts_filled_parameters}"),
                ("human", "{footer}"),
            ]
        )

        chain = create_structured_output_chain(trigger_event_class, self.llm, prompt, verbose=True)
        response:trigger_event_class = chain.run(
            agent_name = self.agent_state.name,
            agent_description = self.agent_state.description,
            agent_world_state=self.agent_state.host_world_prompt,
            goals=self.agent_state.goals,
            plan=self.agent_state.plan,
            memory=self.agent_state.last_retrieved_memory,
            other_thoughts_filled_parameters=self.agent_state.other_thoughts_filled_parameters,
            footer="""Fill the parameters of the triggering event based on the previous context that you have about the world.
            """,
        )

        return response
