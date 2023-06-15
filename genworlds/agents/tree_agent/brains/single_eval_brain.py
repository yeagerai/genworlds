from textwrap import dedent
from typing import Optional, Type, TypedDict
from langchain import BasePromptTemplate, PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from genworlds.agents.tree_agent.brains.brain import Brain
from genworlds.agents.tree_agent.prompts.execution_generator_prompt import (
    ExecutionGeneratorPrompt,
)

from langchain.schema import BaseRetriever


class SingleEvalBrain(Brain):
    """This brain generates a number of thoughts and passes them all to the evaluator, which selects one of them."""

    def __init__(
        self,
        openai_api_key: str,
        prompt_template_class: Type[BasePromptTemplate],
        llm_params: list[str],
        generator_role_prompt: str,
        generator_results_prompt: str,
        evaluator_role_prompt: str,
        evaluator_results_prompt: str,
        n_of_thoughts: int,
        model_name="gpt-4",
        temperature=0.7,
        verbose=False,
        request_timeout=120,
    ):
        self.n_of_thoughts = n_of_thoughts
        self.verbose = verbose

        self.prompt_template_class = prompt_template_class
        self.llm_params = llm_params

        llm = ChatOpenAI(
            temperature=temperature,
            openai_api_key=openai_api_key,
            model_name=model_name,
            request_timeout=request_timeout,
        )

        self.gen_prompt = prompt_template_class(
            token_counter=llm.get_num_tokens,
            input_variables=[
                "previous_thoughts",  # iterative
                "num_thoughts",  # num
            ]
            + llm_params,
            ai_role=dedent(generator_role_prompt),
            response_instruction=dedent(generator_results_prompt),
        )

        self.gen_llm_chain = LLMChain(
            prompt=self.gen_prompt,
            llm=llm,
            verbose=verbose,
        )
        self.eval_prompt = prompt_template_class(
            token_counter=llm.get_num_tokens,
            input_variables=[
                "thought_to_evaluate",
            ]
            + llm_params,
            ai_role=dedent(evaluator_role_prompt),
            response_instruction=dedent(evaluator_results_prompt),
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
        llm_params: dict,
    ):
        # prepare the input variables
        response = self.gen_llm_chain.run(
            num_thoughts=num_thoughts,
            previous_thoughts=previous_thoughts,
            **llm_params,
        ).strip()

        if self.verbose:
            print("Generated: " + response)

        return response

    def eval_thoughts(
        self,
        thoughts_to_evaluate: str,
        llm_params: dict,
    ):
        response = self.eval_llm_chain.run(
            thought_to_evaluate=thoughts_to_evaluate,
            **llm_params,
        )

        if self.verbose:
            print("Evaluated: " + response)

        return response

    def run(self, llm_params: dict):
        thoughts = self.gen_thoughts("", self.n_of_thoughts, llm_params)
        if self.n_of_thoughts == 1:
            return thoughts.strip().removeprefix("- ")

        best_thought = self.eval_thoughts(thoughts, llm_params)

        return best_thought
