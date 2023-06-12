from typing import TypedDict
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from genworlds.agents.tree_agent.prompts.execution_generator_prompt import (
    ExecutionGeneratorPrompt,
)
from genworlds.agents.tree_agent.tree_of_thoughts import TreeOfThoughts

from langchain.vectorstores import Chroma
from langchain.schema import BaseRetriever


class PodcastBrain:
    LLMParams = TypedDict(
        "LLMParams",
        {
            # "plan": str,  # iterative
            "goals": list[str],  # fixed by the user list
            "memory": BaseRetriever,  # this is no good, we have to improve it before sending it to the AI, a summary of everything in one paragraph
            "personality_db": Chroma | None,
            "agent_world_state": str,  # listening_antena input
            "nearby_entities": list[str],  # name description and location
            # "inventory": list[str],  # name description
            "command_to_execute": str,
            # "messages": list,
            "previous_brain_outputs": list[str],
        },
    )

    def __init__(
        self,
        openai_api_key,
        generator_role_prompt: str,
        generator_results_prompt: str,
        evaluator_role_prompt: str,
        evaluator_results_prompt: str,
        n_of_thoughts: int,
        value_threshold: float = 0,
        model_name="gpt-4",
        temperature=0.7,
        verbose=False,
    ):
        self.n_of_thoughts = n_of_thoughts
        self.value_threshold = value_threshold
        self.verbose = verbose

        llm = ChatOpenAI(
            temperature=temperature,
            openai_api_key=openai_api_key,
            model_name=model_name,
        )

        self.gen_prompt = ExecutionGeneratorPrompt(
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
        self.eval_prompt = ExecutionGeneratorPrompt(
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

        if self.verbose:
            print("Generated: " + response)
        
        return response

    def eval_thoughts(
        self,
        thoughts_to_evaluate: str,
        llm_params: LLMParams,
    ):
        response = self.eval_llm_chain.run(
            thought_to_evaluate=thoughts_to_evaluate,
            **llm_params,
        )

        if self.verbose:
            print("Evaluated: " + response)
        
        return response

    def run(self, llm_params: LLMParams):        
        thoughts = self.gen_thoughts("", self.n_of_thoughts, llm_params)
        if self.n_of_thoughts == 1:
            return thoughts.strip().removeprefix("- ")

        best_thought = self.eval_thoughts(thoughts, llm_params)
        
        return best_thought