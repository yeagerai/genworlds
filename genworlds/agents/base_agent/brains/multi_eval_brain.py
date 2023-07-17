import json
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

class MultiEvalBrain(Brain):
    """This brain generates a number of thoughts, and passes them to the evaluator one by one to be rated.
    It then selects the highest rated thought and returns it, or None if no thought was rated above the threshold.
    """

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
        output_parameter_generator: Callable[[dict], dict[str, dict]],
        value_threshold: float = 0,
        model_name="gpt-4",
        temperature=0.7,
        verbose=False,
        request_timeout=120,
    ):
        self.n_of_thoughts = n_of_thoughts
        self.value_threshold = value_threshold
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
            input_variables=[
                "previous_thoughts",  # iterative
                "num_thoughts",  # num
            ]
            + llm_params,
            ai_role=dedent(generator_role_prompt),
            response_instruction=dedent(generator_results_prompt),
        )

        self.eval_prompt = prompt_template_class(
            token_counter=self.llm.get_num_tokens,
            input_variables=[
                "thought_to_evaluate",
            ]
            + llm_params,
            ai_role=dedent(evaluator_role_prompt),
            response_instruction=dedent(evaluator_results_prompt),
        )

    def gen_thoughts(
        self,
        previous_thoughts,
        num_thoughts: int,
        llm_params: dict,
    ):
        generator_function = {
            "name": "generate_options",
            "description": f"Generates {num_thoughts} options for the agent to choose from.",
            "parameters": {
                "type": "object",
                "properties": {
                    "options": {
                        "type": "array",
                        "minItems": num_thoughts,
                        "maxItems": num_thoughts,
                        "items": {
                            "type": "object",
                            "properties": self.output_parameter_generator(llm_params),
                        }
                    },
                },
                "required": ["options"],
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
            num_thoughts=num_thoughts,
            previous_thoughts=previous_thoughts,
            **llm_params,
        )

        if self.verbose:
            print("Generated: " + str(response))

        return response
    
    def eval_thoughts(
        self,
        thoughts_to_evaluate: list,
        llm_params: dict,
    ):
        thought_values = {}

        for thought in thoughts_to_evaluate:
            evaluator_function = {
                "name": "evaluate_output",
                "description": "Evaluate the output of the generator.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "number",
                        },
                    },                        
                    "required": ["value"],
                },
            }

            llm_kwargs = get_llm_kwargs(evaluator_function)
            output_parser = JsonOutputFunctionsParser()

            eval_llm_chain = LLMChain(
                prompt=self.eval_prompt,
                llm=self.llm,
                llm_kwargs=llm_kwargs,
                output_parser=output_parser,
                verbose=self.verbose,
            )

            response = eval_llm_chain.run(
                thought_to_evaluate=json.dumps(thought),
                **llm_params,
            )

            thought_values[thought] = response["value"]

        if self.verbose:
                print("Evaluated: " + str(thought_values))

        return thought_values

    def run(self, llm_params: dict):
        thoughts = self.gen_thoughts("", self.n_of_thoughts, llm_params)
        if self.n_of_thoughts == 1 and self.value_threshold == 0:
            return thoughts[0]

        thought_values = self.eval_thoughts(thoughts, llm_params)

        if self.verbose:
            print("Evaluated: ", thought_values)

        best_thought = max(thought_values, key=thought_values.get)

        if thought_values[best_thought] < self.value_threshold:
            return None
        else:
            return best_thought
