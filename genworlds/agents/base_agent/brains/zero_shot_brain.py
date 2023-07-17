from textwrap import dedent
from typing import Callable, Optional, Type, TypedDict
from langchain import BasePromptTemplate, PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from genworlds.agents.base_agent.brains.brain import Brain
from genworlds.agents.base_agent.prompts.execution_generator_prompt import (
    ExecutionGeneratorPrompt,
)

from langchain.output_parsers.openai_functions import JsonKeyOutputFunctionsParser, JsonOutputFunctionsParser
from langchain.chains.openai_functions.utils import get_llm_kwargs

class ZeroShotBrain(Brain):
    """This brain generates one output and returns it."""

    def __init__(
        self,
        openai_api_key: str,
        prompt_template_class: Type[BasePromptTemplate],
        llm_params: list[str],
        generator_role_prompt: str,
        generator_results_prompt: str,
        output_parameter_generator: Callable[[dict], dict[str, dict]],
        model_name="gpt-4",
        temperature=0.7,
        verbose=False,
        request_timeout=120,
    ):
        self.verbose = verbose

        self.prompt_template_class = prompt_template_class
        self.llm_params = llm_params

        self.output_parameter_generator = output_parameter_generator

        self.llm = ChatOpenAI(
            temperature=temperature,
            openai_api_key=openai_api_key,
            model_name=model_name,
            request_timeout=request_timeout,
        )

        self.gen_prompt = prompt_template_class(
            token_counter=self.llm.get_num_tokens,
            input_variables=llm_params,
            ai_role=dedent(generator_role_prompt),
            response_instruction=dedent(generator_results_prompt),
        )

    def gen_thoughts(
        self,
        llm_params: dict,
    ):
        output_parameters = self.output_parameter_generator(llm_params)

        generator_function = {
            "name": "generate_output",
            "description": f"Generates the desired output parameters.",
            "parameters": {
                "type": "object",
                "properties": output_parameters,
                "required": list(output_parameters.keys()),
            },
        }


        llm_kwargs = get_llm_kwargs(generator_function)
        output_parser = JsonKeyOutputFunctionsParser(key_name="options")

        if self.verbose:
            print(llm_kwargs)

        gen_llm_chain = LLMChain(
            prompt=self.gen_prompt,
            llm=self.llm,
            llm_kwargs=llm_kwargs,
            output_parser=output_parser,
            verbose=self.verbose,
        )

        # prepare the input variables
        response = gen_llm_chain.run(
            **llm_params,
        )

        if self.verbose:
            print("Generated: " + str(response))

        return response

    def run(self, llm_params: dict):
        return self.gen_thoughts(llm_params)
