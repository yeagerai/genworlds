import os
import re
from typing import List
from pydantic import BaseModel

from yeagerai.toolkit.yeagerai_tool import YeagerAITool

from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from yeagerai.toolkit.create_tool_source.create_tool_master_prompt import (
    CREATE_TOOL_MASTER_PROMPT,
)


class RandomlyWalkAPIWrapper(BaseModel):
    world_size: List[float] = [100, 100, 100]
    agent_positon: List[float] = [0, 0, 0]
    exploration_radius: int = 20

    def run(self, explored_zones: str) -> str:
        pass


class RandomlyWalkRun(YeagerAITool):
    """Tool that adds the capability of creating the source code of other Tools on-the-fly and writing it into cwd."""

    name = "Create Tool Source"
    description = """Useful for when you need to create the source code of a YeagerAITool. 
        Input MUST BE a string made of two substrings separated by a this token '######SPLIT_TOKEN########'.
        That is substring1+'######SPLIT_TOKEN########'+substring2: 
        - where substring1 represents the first string represents the solution sketch of the functionality wanted in the Tool.
        - and substring 2 is code block that contains the tool_tests. That is the unit tests already created for testing the tool. 
        Both of them should be defined earlier in the conversation.
        """
    final_answer_format = "Final answer: just return a success message saying the path where the class was written"
    api_wrapper: RandomlyWalkAPIWrapper

    def _run(self, solution_sketch_n_tool_tests: str) -> str:
        """Use the tool."""
        return self.api_wrapper.run(
            solution_sketch_n_tool_tests=solution_sketch_n_tool_tests
        )

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("GoogleSearchRun does not support async")
