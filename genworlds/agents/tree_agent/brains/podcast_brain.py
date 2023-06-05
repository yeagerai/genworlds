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
                "previous_thoughts",  # iterative
                "num_thoughts",  # num
            ]
            + list(self.LLMParams.__annotations__.keys()),
            ai_role="You are {ai_name}, an expert podcaster. You have to generate a podcast response based on:".format(
                ai_name=ai_name
            ),
            response_instruction="""# Response type
                {num_thoughts} paragraphs of text containing a speech that achieves your desired goal, contributes to the conversation and matches something you would say AND NOTHING ELSE:
                - The first possible paragraph
                - A second possible paragraph
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
            ai_role="You are {ai_name}, an expert in evaluating the quality and the depth of a podcast response based on:".format(
                ai_name=ai_name
            ),
            response_instruction="""## Thought to evaluate
                Evaluate the following thought by rating it from 0 to 1, where 0 means that the thought is not useful at all, and 1 means that the thought is very useful:
                {thought_to_evaluate}

                # Response type
                Return the evaluation of the thought as a float between 0 and 1, and NOTHING ELSE:      
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
