import json
import time
from typing import Any, Callable, List, Optional

from pydantic import BaseModel

from genworlds.agents.yeager_autogpt.prompt_generator import get_prompt
from langchain.prompts.chat import (
    BaseChatPromptTemplate,
)
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.tools.base import BaseTool
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.vectorstores import Qdrant


class AutoGPTPrompt(BaseChatPromptTemplate, BaseModel):
    ai_name: str
    ai_role: str
    tools: List[BaseTool]
    token_counter: Callable[[str], int]
    send_token_limit: int = 8192

    def construct_full_prompt(self, agent_world_state: str, goals: List[str]) -> str:
        prompt_start = (
            "Your decisions must always be made independently "
            "without seeking user assistance.\n"
            "Play to your strengths as an LLM and pursue simple "
            "strategies with no legal complications.\n"
            "If you have completed all your tasks, make sure to "
            'use the "finish" command.'
            "\n\n"
            "You are an agent that lives in a world with other agents and objects.\n"
            "You can move around the world, interact with objects, and talk to other agents.\n"
            "You have an inventory that can hold objects.\n"
        )

        # Add agent world state
        prompt_start += agent_world_state

        # Construct full prompt
        full_prompt = (
            f"You are {self.ai_name}, {self.ai_role}\n{prompt_start}\n\nGOALS:\n\n"
        )
        for i, goal in enumerate(goals):
            full_prompt += f"{i+1}. {goal}\n"

        full_prompt += f"\n\n{get_prompt(self.tools)}"
        return full_prompt

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        messages: List[BaseMessage] = []

        base_prompt = SystemMessage(
            content=self.construct_full_prompt(
                kwargs["agent_world_state"], kwargs["goals"]
            )
        )
        messages.append(base_prompt)

        time_prompt = SystemMessage(
            content=f"The current time and date is {time.strftime('%c')}"
        )
        messages.append(time_prompt)
        used_tokens = self.token_counter(base_prompt.content) + self.token_counter(
            time_prompt.content
        )

        inventory = kwargs["inventory"]
        if len(inventory) > 0:
            inventory_prompt = f"You have the following items in your inventory:\n"
            for entity in inventory:
                inventory_prompt += f"{json.dumps(entity)}\n"
        else:
            inventory_prompt = f"You have no items in your inventory.\n"
        inventory_message = SystemMessage(content=inventory_prompt)
        messages.append(inventory_message)
        used_tokens += self.token_counter(inventory_message.content)

        nearby_entities = kwargs["nearby_entities"]
        if len(nearby_entities) > 0:
            nearby_entities_prompt = f"There are the following entities near you: \n"
            for entity in nearby_entities:
                nearby_entities_prompt += f"{json.dumps(entity)}\n"
        else:
            nearby_entities_prompt = f"There are no entities near you.\n"
        nearby_entities_message = SystemMessage(content=nearby_entities_prompt)
        messages.append(nearby_entities_message)
        used_tokens += self.token_counter(nearby_entities_message.content)

        relevant_commands = kwargs["relevant_commands"]
        relevant_commands_prompt = f'You can perform the following additional commands with the entities nearby. "target_id" is the id of the entity that provides the command:\n'
        for command in relevant_commands:
            relevant_commands_prompt += f"{command}\n"
        relevant_commands_message = SystemMessage(content=relevant_commands_prompt)
        messages.append(relevant_commands_message)
        used_tokens += self.token_counter(relevant_commands_message.content)

        personality_db: Qdrant = kwargs["personality_db"]
        if personality_db is not None:
            previous_messages = kwargs["messages"]
            past_statements = list(
                map(
                    lambda d: d.page_content,
                    personality_db.similarity_search(str(previous_messages[-10:])),
                )
            )
            if len(past_statements) > 0:
                past_statements_format = f"You have said the following things in the past on this topic:\n{past_statements}\n\n"
                personality_message = SystemMessage(content=past_statements_format)
                messages.append(personality_message)
                used_tokens += len(personality_message.content)

        memory: VectorStoreRetriever = kwargs["memory"]
        previous_messages = kwargs["messages"]
        relevant_docs = memory.get_relevant_documents(str(previous_messages[-10:]))
        relevant_memory = [d.page_content for d in relevant_docs]
        relevant_memory_tokens = sum(
            [self.token_counter(doc) for doc in relevant_memory]
        )
        while used_tokens + relevant_memory_tokens > 2500:
            relevant_memory = relevant_memory[:-1]
            relevant_memory_tokens = sum(
                [self.token_counter(doc) for doc in relevant_memory]
            )
        content_format = (
            f"This reminds you of these events "
            f"from your past:\n{relevant_memory}\n\n"
        )
        memory_message = SystemMessage(content=content_format)
        messages.append(memory_message)
        used_tokens += len(memory_message.content)

        # historical_messages: List[BaseMessage] = []
        # for message in previous_messages[-10:][::-1]:
        #     message_tokens = self.token_counter(message.content)
        #     if used_tokens + message_tokens > self.send_token_limit - 1000:
        #         break
        #     historical_messages = [message] + historical_messages
        # input_message = HumanMessage(content=kwargs["user_input"])

        # messages += historical_messages
        # plan: Optional[str] = kwargs["plan"]

        # messages.append(input_message)
        return messages
