---
sidebar_position: 2
---

# Thought Actions

Thought actions are a special type of action that agents can trigger. They are non-deterministic actions that can be triggered by agents to fill event parameters with non deterministic information.

Here is the abstract interface that all thought actions must implement:

```python
class ThoughtAction(AbstractAction):
    """
    Abstract interface class for a Thought Action.

    This includes the list of thoughts required to fill the parameters of the trigger event.
    """

    # {parameter_name: [thought_class, run_dict]}
    required_thoughts: Dict[str, Tuple[AbstractThought, dict]]
```

By adding a thought action to an agent, you can fill event parameters in a non-deterministic way. So before the agent fills the event that will send to the socket, it will look for the thoughts that it has to execute to fill some of the event parameters. And will execute those thoughts before going to the `event_filler_thought`.

So to understand better what thought actions can do, we have to understand what a thought is.

## Thoughts

Are esentially LLM calls that can be triggered by agents to fill event parameters with non deterministic information.

Here is an example, the thought that we tipically use in `RAG` simulated worlds, to answer the user's question based on the data extracted from the different data structures:

```python
class JustifiedAnswer(BaseModel):
    """Answers the user's question based on data extracted from different data structures."""

    answer: str = Field(
        ...,
        description="The final answer to the user.",
    )
    rationale: str = Field(
        ...,
        description="The rationale of why this is the correct answer to user's question.",
    )
    references: Optional[List[str]] = Field(
        ..., description="References to documents extracted from metadata."
    )

class AnswerFromSourcesThought(AbstractThought):
    def __init__(
        self,
        agent_state: AbstractAgentState # other thoughts unique init arg, so everything goes through state
    ):
        self.agent_state = agent_state
        self.llm = ChatOpenAI(
            model="gpt-4", openai_api_key=openai_api_key, temperature=0.1
        )

    def run(self):
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
                    "This is the last user's question: \n{user_question}",
                ),
                (
                    "system",
                    "This is relevant information related to the user's question: \n{relevant_info}",
                ),
                ("human", "{footer}"),
            ]
        )

        chain = create_structured_output_chain(
            output_schema=JustifiedAnswer.schema(),
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
            user_question=self.agent_state.users_question,
            relevant_info=self.agent_state.retrieved_information_from_data_structures,
            footer="""Provide a justified answer to user's question based on the different data structures, the rationale, and references when possible.
            """,
        )
        response = JustifiedAnswer.parse_obj(response)
        return response
```

In this thought, we use LangChain and OpenAI Function calling to fill the `answer` and `rationale` parameters of the `JustifiedAnswer` schema by calling `gpt-3.5-turbo`.

## When to use thought actions

For simple interactions with objects and other agents, you don't need to create specific thought actions, as the decisions are being made by the `action_schema_selector_thought` and the `event_filler_thought`.

But when you need to fill event parameters with non-deterministic information, you can create a thought action that will be triggered by the agent to fill those parameters.

By enhancing the `BasicAssistant` capabilities with more actions and thought actions, you can create more complex agents that probably cover most of the use cases that you will encounter.

## Action Chains

Action chains are chains of actions that are executed sequentially. They are used to avoid the agent to be constantly selecting actions when we already know how the procedure should be in advance. It's a way to make the agent more efficient and avoid potential errors of the `action_shema_selector_thought`.
