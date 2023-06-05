from typing import TypedDict
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from genworlds.agents.tree_agent.prompts.navigation_generator_prompt import (
    NavigationGeneratorPrompt,
)

from genworlds.agents.tree_agent.tree_of_thoughts import TreeOfThoughts

from langchain.vectorstores import Chroma
from langchain.schema import BaseRetriever


class NavigationBrain:
    LLMParams = TypedDict(
        "LLMParams",
        {
            "plan": str,  # iterative
            "goals": list[str],  # fixed by the user list
            "memory": BaseRetriever,  # this is no good, we have to improve it before sending it to the AI, a summary of everything in one paragraph
            "personality_db": Chroma | None,
            "agent_world_state": str,  # listening_antena input
            "nearby_entities": list[str],  # name description and location
            "inventory": list[str],  # name description
            "relevant_commands": list[
                str
            ],  # just the event types, and the description of what the event does (not even the name)
            "messages": list,
        },
    )

    def __init__(
        self,
        openai_api_key: str,
        ai_name: str,
        model_name="gpt-3.5-turbo",
        search_algorithm="BFS",
    ):
        self.search_algorithm = search_algorithm
        self.tot = TreeOfThoughts(
            gen_thoughts=self.gen_thoughts,
            eval_thoughts=self.eval_thoughts,
            search_algorithm=self.search_algorithm,
            initial_state="",
            thought_limit=3,
            max_depth=1,
            breadth=1,
            value_threshold=0.5,
        )
        llm = ChatOpenAI(
            temperature=0, openai_api_key=openai_api_key, model_name=model_name
        )

        self.gen_prompt = NavigationGeneratorPrompt(
            token_counter=llm.get_num_tokens,
            input_variables=[
                "previous_thoughts",  # iterative
                "num_thoughts",  # num
            ]
            + list(self.LLMParams.__annotations__.keys()),
            ai_role="You are {ai_name}. You need to choose your next action that helps you achieve your goals. It must be consistent with all of the following information:".format(
                ai_name=ai_name
            ),
            response_instruction="""# Response type
                A bullet list containing {num_thoughts} of possible plans and next events that help you achieve your large scale goals. You can use the same event multiple times with different goals in mind. If none of the actions make sense, you can also use the action "Self:wait". Use the following format:
                - {{ "plan": "1. plan step 1 2. plan step 2 3. plan step 3", "next_action": "Class:event_type_1", "goal": "I want to use this event to achieve a goal"}}
                - {{ "plan": "1. plan step 1 2. plan step 2 3. plan step 3", "next_action": "Class:event_type_1", "goal": "I want to use this event to achieve a different goal"}}
                - {{ "plan": "1. plan step 1 2. plan step 2 3. plan step 3"", "next_action": "Class:event_type_2", "goal": "I want to use this event to achieve a third goal"}}
            """,
        )

        self.gen_llm_chain = LLMChain(
            prompt=self.gen_prompt,
            llm=llm,
            verbose=True,
        )

        self.eval_prompt = NavigationGeneratorPrompt(
            token_counter=llm.get_num_tokens,
            input_variables=[
                "thought_to_evaluate",
            ]
            + list(self.LLMParams.__annotations__.keys()),
            ai_role="You are {ai_name}, an expert in evaluating which events get you closer to achieving your goals based on:".format(
                ai_name=ai_name
            ),
            response_instruction="""## Action to evaluate
                Evaluate the following plan by rating it from 0 to 1, where 0 means that the plan is not useful or possible, and 1 means that the plan is the best next step you can take:
                {thought_to_evaluate}

                # Response type
                Return the evaluation of the plan as a float between 0 and 1, and NOTHING ELSE:
            """,
        )

        self.eval_llm_chain = LLMChain(
            prompt=self.eval_prompt,
            llm=llm,
            verbose=True,
        )

    def gen_thoughts(
        self,
        previous_thoughts,
        num_thoughts: int,
        llm_params: LLMParams,
    ):
        # prepare the input variables
        response = self.gen_llm_chain.run(
            num_thoughts=num_thoughts,
            previous_thoughts=previous_thoughts,
            **llm_params,
        )

        return list(map(lambda s: s.removeprefix("- "), response.strip().split("\n")))

    def eval_thoughts(
        self,
        thoughts_to_evaluate: list[str],
        llm_params: LLMParams,
    ):
        thought_values = {}

        for thought in thoughts_to_evaluate:
            response = self.eval_llm_chain.run(
                thought_to_evaluate=thought,
                **llm_params,
            )

            try:
                thought_values[thought] = float(response)
            except:
                thought_values[thought] = 0

        print(thought_values)

        return thought_values

    def run(self, llm_params: LLMParams):
        return self.tot.solve(llm_params)[-1]
