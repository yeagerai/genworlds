import json
import time
from typing import Any, Callable, List, Optional

from pydantic import BaseModel

from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.tools.base import BaseTool
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.vectorstores import VectorStore
from langchain.prompts.chat import (
    BaseChatPromptTemplate,
)

from genworlds.agents.memories.simulation_memory import SimulationMemory


class ExecutionGeneratorPrompt(BaseChatPromptTemplate, BaseModel):
    ai_role: str
    response_instruction: str
    token_counter: Callable[[str], int]
    send_token_limit: int = 8192

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

        if (
            "previous_brain_outputs" in kwargs
            and len(kwargs["previous_brain_outputs"]) > 0
        ):
            previous_brain_outputs_prompt = f"## Previous thoughts:\n"

            for entity in kwargs["previous_brain_outputs"]:
                previous_brain_outputs_prompt += f"- {json.dumps(entity)}\n"

            previous_brain_outputs_message = SystemMessage(
                content=previous_brain_outputs_prompt
            )
            messages.append(previous_brain_outputs_message)
            used_tokens += self.token_counter(previous_brain_outputs_message.content)

        time_prompt = SystemMessage(
            content=f"The current time and date is {time.strftime('%c')}"
        )
        messages.append(time_prompt)
        used_tokens = self.token_counter(base_prompt.content) + self.token_counter(
            time_prompt.content
        )

        if "inventory" in kwargs:
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

        if "all_entities" in kwargs:
            all_entities = kwargs["all_entities"]
            all_entities_prompt = f"## All entities: \n"
            if len(all_entities) > 0:
                for entity in all_entities:
                    all_entities_prompt += f"{json.dumps(entity)}\n"
            else:
                all_entities_prompt += f"There are no entities.\n"
            all_entities_message = SystemMessage(content=all_entities_prompt)
            messages.append(all_entities_message)
            used_tokens += self.token_counter(all_entities_message.content)

        if "command_to_execute" in kwargs:
            command_to_execute = kwargs["command_to_execute"]["string_full"]
            command_to_execute_message = SystemMessage(
                content=f"## You have selected the following command to execute:\n{command_to_execute}"
            )
            messages.append(command_to_execute_message)
            used_tokens += len(command_to_execute_message.content)

        if "plan" in kwargs:
            plan = "\n".join(
                [f"{i+1}. {goal}" for i, goal in enumerate(kwargs["plan"])]
            )
            plan_message = SystemMessage(content=f"## Your Plan:\n{plan}")
            messages.append(plan_message)
            used_tokens += len(plan_message.content)

        if "personality_db" in kwargs and kwargs["personality_db"] is not None:
            personality_db: VectorStore = kwargs["personality_db"]
            past_statements = [
                document.page_content
                for document in personality_db.similarity_search(
                    str(kwargs["previous_brain_outputs"][-1])
                )
            ]

            if len(past_statements) > 0:
                past_statements_bullet_list = "\n".join(
                    map(lambda s: f"- {s}", past_statements)
                )
                past_statements_format = f"You have said the following things on this topic in the past:\n{past_statements_bullet_list}\n\n"
                personality_message = SystemMessage(content=past_statements_format)
                messages.append(personality_message)
                used_tokens += len(personality_message.content)

        if "memory" in kwargs and kwargs["memory"] is not None:
            memory: SimulationMemory = kwargs["memory"]
            if len(memory.world_events) > 0:
                if len(memory.world_events) % 5 == 0:
                    memory.create_full_summary()
                relevant_memory = memory.get_event_stream_memories(
                    query=kwargs["previous_brain_outputs"][-1], summarized=False
                )  # TODO: add token limitations
                relevant_memory_tokens = self.token_counter(relevant_memory)
                memory_message = SystemMessage(content=relevant_memory)
                messages.append(memory_message)
                used_tokens += relevant_memory_tokens

        instruction = HumanMessage(content=self.response_instruction.format(**kwargs))
        messages.append(instruction)

        return messages
