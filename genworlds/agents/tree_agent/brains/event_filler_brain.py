from typing import Optional, TypedDict
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from genworlds.agents.tree_agent.prompts.execution_generator_prompt import (
    ExecutionGeneratorPrompt,
)
from genworlds.agents.tree_agent.tree_of_thoughts import TreeOfThoughts

from langchain.vectorstores import Chroma
from langchain.schema import BaseRetriever


class EventFillerBrain:
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
            "command_to_execute": dict,
            "messages": list,
            "previous_brain_outputs": list[str],
        },
    )

    def __init__(
        self,
        openai_api_key,
        ai_name: str,
        model_name="gpt-3.5-turbo",
        search_algorithm="BFS",
    ):
        self.search_algorithm = search_algorithm
        self.tot = TreeOfThoughts(
            self.gen_thoughts,
            self.eval_thoughts,
            self.search_algorithm,
            initial_state="",
            thought_limit=1,
            max_depth=1,
            breadth=1,
            value_threshold=0.5,
        )

        llm = ChatOpenAI(
            temperature=0, openai_api_key=openai_api_key, model_name=model_name
        )

        self.gen_prompt = ExecutionGeneratorPrompt(
            token_counter=llm.get_num_tokens,
            input_variables=[
                "previous_thoughts",  # TODO: take out
                "num_thoughts",
            ]
            + list(self.LLMParams.__annotations__.keys()),
            ai_role="""You are {ai_name}. In previous steps, you have selected an action to execute, and possibly generated some of the response parameters in a previous step - make sure to include those exactly. 
                You now need to generate a valid set of JSON parameters for the command to execute, based on the following information:
            """.format(
                ai_name=ai_name
            ),
            response_instruction="""# Response type
                {num_thoughts} lines of json containing possible options for completing the arguments of the command to execute, each one with the following format AND NOTHING ELSE:
                - {{"arg name": "value1", "arg name 2": "value2", ...}}
                - {{"arg name": "alt value1", "arg name 2": "alt value2", ...}} 
            """,
        )

        self.gen_llm_chain = LLMChain(
            prompt=self.gen_prompt,
            llm=llm,
            verbose=True,
        )
        self.eval_prompt = ExecutionGeneratorPrompt(
            token_counter=llm.get_num_tokens,
            input_variables=[
                "thought_to_evaluate",
            ]
            + list(self.LLMParams.__annotations__.keys()),
            ai_role="You are {ai_name}. You need to evaluate the provided set of JSON parameters based on their correctness, with respect to all of the following information:".format(
                ai_name=ai_name
            ),
            response_instruction="""## Parameters to evaluate
                Evaluate the following set of parameters by rating them from 0 to 1, where 0 means that the parameters are not correct, and 1 means that the parameters completely correct:
                {thought_to_evaluate}

                # Response type
                Return the evaluation of the parameters as a float between 0 and 1, and NOTHING ELSE:      
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

        return thought_values

    def run(self, llm_params: LLMParams):
        return self.tot.solve(llm_params)[0]
