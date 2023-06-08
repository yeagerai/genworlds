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
from langchain.vectorstores import Chroma


class NavigationGeneratorPrompt(BaseChatPromptTemplate, BaseModel):
    ai_role: str
    response_instruction: str
    token_counter: Callable[[str], int]
    send_token_limit: int = 4196

    basic_template = """
        # Basic rules
        {ai_role}

        ## Your Goals
        {goals}

        ## World State
        {agent_world_state}
        """

    def construct_full_prompt(self, agent_world_state: str, goals: List[str]) -> str:
        return self.basic_template.format(
            ai_role=self.ai_role,
            goals="\n".join([f"{i+1}. {goal}" for i, goal in enumerate(goals)]),
            agent_world_state=agent_world_state,
        )

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        kwargs = {key: kwargs[key] for key in self.input_variables}

        messages: List[BaseMessage] = []

        base_prompt = SystemMessage(
            content=self.construct_full_prompt(
                kwargs["agent_world_state"], kwargs["goals"]
            )
        )
        messages.append(base_prompt)
        used_tokens = self.token_counter(base_prompt.content)

        
        if "previous_thoughts" in kwargs and len(kwargs["previous_thoughts"]) > 0:
            previous_thoughts_prompt = f"## Previous thoughts:\n"
            for entity in kwargs["previous_thoughts"]:
                previous_thoughts_prompt += f"- {json.dumps(entity)}\n"

            previous_thoughts_message = SystemMessage(content=previous_thoughts_prompt)
            messages.append(previous_thoughts_message)
            used_tokens += self.token_counter(previous_thoughts_message.content)
        

        # time_prompt = SystemMessage(
        #     content=f"The current time and date is {time.strftime('%c')}"
        # )
        # messages.append(time_prompt)
        # used_tokens = self.token_counter(base_prompt.content) + self.token_counter(
        #     time_prompt.content
        # )

        inventory = kwargs["inventory"]
        inventory_prompt = f"## Inventory:\n"
        if len(inventory) > 0:
            for entity in inventory:
                inventory_prompt += f"- {json.dumps(entity)}\n"
        else:
            inventory_prompt += f"You have no items in your inventory.\n"
        inventory_message = SystemMessage(content=inventory_prompt)
        messages.append(inventory_message)
        used_tokens += self.token_counter(inventory_message.content)

        nearby_entities = kwargs["nearby_entities"]
        nearby_entities_prompt = f"## Nearby entities: \n"
        if len(nearby_entities) > 0:
            for entity in nearby_entities:
                nearby_entities_prompt += f"{json.dumps(entity)}\n"
        else:
            nearby_entities_prompt += f"There are no entities near you.\n"
        nearby_entities_message = SystemMessage(content=nearby_entities_prompt)
        messages.append(nearby_entities_message)
        used_tokens += self.token_counter(nearby_entities_message.content)

        if "relevant_commands" in kwargs and len(kwargs["relevant_commands"]) > 0:
            relevant_commands = kwargs["relevant_commands"]
            relevant_commands_prompt = f"You can perform the following actions with the entities nearby:\n"
            for command in relevant_commands:
                relevant_commands_prompt += f"{command}\n"
            relevant_commands_message = SystemMessage(content=relevant_commands_prompt)
            messages.append(relevant_commands_message)
            used_tokens += self.token_counter(relevant_commands_message.content)

        if "plan" in kwargs and kwargs["plan"] is not None:
            plan: Optional[str] = kwargs["plan"]
            plan_message = SystemMessage(content=f"## My Previous Plan:\n{plan}")
            messages.append(plan_message)
            used_tokens += len(plan_message.content)

        personality_db: Chroma = kwargs["personality_db"]
        if personality_db is not None:
            past_statements = list(
                map(
                    lambda d: d.page_content,
                    personality_db.similarity_search(str(kwargs["goals"])),
                )
            )
            if len(past_statements) > 0:
                past_statements_format = f"You have said the following things in the past on this topic:\n{past_statements}\n\n"
                personality_message = SystemMessage(content=past_statements_format)
                messages.append(personality_message)
                used_tokens += len(personality_message.content)

        memory: VectorStoreRetriever = kwargs["memory"]
        relevant_docs = memory.get_relevant_documents(str(kwargs["goals"]))
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
        # previous_messages = kwargs["messages"]
        # for message in previous_messages[-10:][::-1]:
        #     message_tokens = self.token_counter(message.content)
        #     if used_tokens + message_tokens > self.send_token_limit - 1000:
        #         break
        #     historical_messages = [message] + historical_messages

        # messages += historical_messages

        instruction = HumanMessage(content=self.response_instruction.format(**kwargs))
        messages.append(instruction)

        return messages
