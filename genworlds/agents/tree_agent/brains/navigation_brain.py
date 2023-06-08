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
        generator_role_prompt: str,
        generator_results_prompt: str,
        evaluator_role_prompt: str,
        evaluator_results_prompt: str,
        n_of_thoughts: int,
        value_threshold: float = 0.5,
        model_name="gpt-4",
        temperature=0.7,
        verbose=False,
    ):
        self.n_of_thoughts = n_of_thoughts
        self.value_threshold = value_threshold
        
        llm = ChatOpenAI(
            temperature=temperature, openai_api_key=openai_api_key, model_name=model_name
        )

        self.gen_prompt = NavigationGeneratorPrompt(
            token_counter=llm.get_num_tokens,
            input_variables=[
                "previous_thoughts",  # iterative
                "num_thoughts",  # num
            ]
            + list(self.LLMParams.__annotations__.keys()),
            ai_role=generator_role_prompt,
            response_instruction=generator_results_prompt,
        )

        self.gen_llm_chain = LLMChain(
            prompt=self.gen_prompt,
            llm=llm,
            verbose=verbose,
        )

        self.eval_prompt = NavigationGeneratorPrompt(
            token_counter=llm.get_num_tokens,
            input_variables=[
                "thought_to_evaluate",
            ]
            + list(self.LLMParams.__annotations__.keys()),
            ai_role=evaluator_role_prompt,
            response_instruction=evaluator_results_prompt,
        )

        self.eval_llm_chain = LLMChain(
            prompt=self.eval_prompt,
            llm=llm,
            verbose=verbose,
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
        thoughts = self.gen_thoughts("", self.n_of_thoughts, llm_params)
        thought_values = self.eval_thoughts(thoughts, llm_params)
        print(thought_values)

        best_thought = max(thought_values, key=thought_values.get)

        if thought_values[best_thought] < self.value_threshold:
            return None
        else:
            return best_thought


