from textwrap import dedent
from typing import Optional, Type, TypedDict
from langchain import BasePromptTemplate, PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from genworlds.agents.tree_agent.brains.brain import Brain
from genworlds.agents.tree_agent.prompts.execution_generator_prompt import (
    ExecutionGeneratorPrompt,
)

from langchain.vectorstores import Chroma
from langchain.schema import BaseRetriever


class ZeroShotBrain(Brain):
    """This brain generates one output and returns it."""

    def __init__(
        self,
        openai_api_key: str,
        prompt_template_class: Type[BasePromptTemplate],
        llm_params: list[str],
        generator_role_prompt: str,
        generator_results_prompt: str,
        model_name="gpt-4",
        temperature=0.7,
        verbose=False,
        request_timeout=120,
    ):
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
            input_variables=llm_params,
            ai_role=dedent(generator_role_prompt),
            response_instruction=dedent(generator_results_prompt),
        )

        self.gen_llm_chain = LLMChain(
            prompt=self.gen_prompt,
            llm=llm,
            verbose=verbose,
        )

    def gen_thoughts(
        self,
        llm_params: dict,
    ):
        # prepare the input variables
        response = self.gen_llm_chain.run(
            **llm_params,
        ).strip()

        if self.verbose:
            print("Generated: " + response)
        
        return response

    def run(self, llm_params: dict):        
        return  self.gen_thoughts(llm_params)
