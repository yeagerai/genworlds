from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from time import sleep
import asyncio
from typing import List, Optional

from pydantic import ValidationError

import faiss
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.agents import Tool
from langchain.tools.human.tool import HumanInputRun
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.llm import LLMChain
from langchain.schema import (
    AIMessage,
    BaseMessage,
    Document,
    HumanMessage,
    SystemMessage,
)

from yeager_core.agents.yeager_autogpt.output_parser import AutoGPTOutputParser
from yeager_core.agents.yeager_autogpt.prompt import AutoGPTPrompt
from yeager_core.agents.yeager_autogpt.prompt_generator import FINISH_NAME
from yeager_core.sockets.world_socket_client import WorldSocketClient
from yeager_core.agents.yeager_autogpt.listening_antena import ListeningAntena
from yeager_core.events.base_event import EventHandler, EventDict
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.events.basic_events import (
    AgentMoveToPositionEvent,
    AgentGetsWorldObjectsInRadiusEvent,
    AgentGetsWorldAgentsInRadiusEvent,
    AgentGetsObjectInfoEvent,
    AgentGetsAgentInfoEvent,
    AgentSpeaksWithAgentEvent,
)


class YeagerAutoGPT:
    """Agent class for interacting with Auto-GPT."""

    def __init__(
        self,
        ai_name: str,
        description: str,
        goals: List[str],
        important_event_types: List[str],
        event_dict: EventDict,
        event_handler: EventHandler,
        position: Coordinates,
        size: Size,
        vision_radius: int,
        openai_api_key: str,
        feedback_tool: Optional[HumanInputRun] = None,
        additional_memories: Optional[List[VectorStoreRetriever]] = None,
    ):
        # Its own properties
        self.id = str(uuid4())
        self.ai_name = ai_name
        self.description = description
        self.goals = goals
        self.world_spawned_id = None

        # Event properties
        self.important_event_types = important_event_types
        important_event_types.extend(
            [
                "agent_move_to_position",
                "agent_gets_world_objects_in_radius",
                "agent_gets_world_agents_in_radius",
                "agent_gets_object_info",
                "agent_gets_agent_info",
                "agent_interacts_with_object",
                "agent_interacts_with_agent",
            ]
        )

        self.event_dict = event_dict

        # Phisical world properties
        self.position = position
        self.size = size
        self.vision_radius = vision_radius
        self.world_socket_client = WorldSocketClient()
        self.listening_antena = ListeningAntena(
            self.world_socket_client,
            self.important_event_types,
            agent_name=self.ai_name,
            agent_id=self.id,
        )

        # Agent actions
        self.actions = [
            Tool(
                name="move",
                description="Moves the agent to a position.",
                func=self.agent_move_to_position_action,
            ),
            Tool(
                name="get_objects_in_radius",
                description="Gets the objects in a radius.",
                func=self.agent_gets_world_objects_in_radius_action,
            ),
            Tool(
                name="get_agents_in_radius",
                description="Gets the agents in a radius.",
                func=self.agent_gets_world_agents_in_radius_action,
            ),
            Tool(
                name="get_object_info",
                description="Gets the info of an object.",
                func=self.agent_gets_object_info_action,
            ),
            Tool(
                name="get_agent_info",
                description="Gets the info of an agent.",
                func=self.agent_gets_agent_info_action,
            ),
            Tool(
                name="interact_with_object",
                description="Interacts with an object.",
                func=self.agent_interacts_with_object_action,
            ),
        ]

        # Brain properties
        embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
        embedding_size = 1536
        index = faiss.IndexFlatL2(embedding_size)
        vectorstore = FAISS(
            embeddings_model.embed_query, index, InMemoryDocstore({}), {}
        )
        self.memory = vectorstore.as_retriever()

        llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4")
        prompt = AutoGPTPrompt(
            ai_name=self.ai_name,
            ai_role=self.description,
            vision_radius=self.vision_radius,
            tools=self.actions,
            input_variables=["memory", "messages", "goals", "user_input"],
            token_counter=llm.get_num_tokens,
        )
        self.chain = LLMChain(llm=llm, prompt=prompt)

        self.full_message_history: List[BaseMessage] = []
        self.next_action_count = 0
        self.output_parser = AutoGPTOutputParser()
        self.feedback_tool = None  # HumanInputRun() if human_in_the_loop else None

    async def think(self):
        print(f" The agent {self.ai_name} is thinking...")
        user_input = (
            "Determine which next command to use, "
            "and respond using the format specified above:"
        )

        while True:
            # Send message to AI, get response
            assistant_reply = self.chain.run(
                goals=self.goals,
                messages=self.full_message_history,
                memory=self.memory,
                user_input=user_input,
            )

            # Print Assistant thoughts
            print(assistant_reply)
            self.full_message_history.append(HumanMessage(content=user_input))
            self.full_message_history.append(AIMessage(content=assistant_reply))

            # Get command name and arguments
            action = self.output_parser.parse(assistant_reply)
            tools = {t.name: t for t in self.actions}
            if action.name == FINISH_NAME:
                return action.args["response"]
            if action.name in tools:
                tool = tools[action.name]
                try:
                    observation = await tool.run(action.args)
                except ValidationError as e:
                    observation = (
                        f"Validation Error in args: {str(e)}, args: {action.args}"
                    )
                except Exception as e:
                    observation = (
                        f"Error: {str(e)}, {type(e).__name__}, args: {action.args}"
                    )
                result = f"Command {tool.name} returned: {observation}"
            elif action.name == "ERROR":
                result = f"Error: {action.args}. "
            else:
                result = (
                    f"Unknown command '{action.name}'. "
                    f"Please refer to the 'COMMANDS' list for available "
                    f"commands and only respond in the specified JSON format."
                )
            ## send result and assistant_reply to the socket

            # If there are any relevant events in the world for this agent, add them to memory
            sleep(3)
            last_events = self.listening_antena.get_last_events()
            memory_to_add = (
                f"Assistant Reply: {assistant_reply} "
                f"\nResult: {result} "
                f"\nLast World Events: {last_events}"
            )

            if self.feedback_tool is not None:
                feedback = f"\n{self.feedback_tool.run('Input: ')}"
                if feedback in {"q", "stop"}:
                    print("EXITING")
                    return "EXITING"
                memory_to_add += feedback

            self.memory.add_documents([Document(page_content=memory_to_add)])
            self.full_message_history.append(SystemMessage(content=result))

    async def agent_move_to_position_action(self, new_position: Coordinates):
        agent_new_position = AgentMoveToPositionEvent(
            created_at=datetime.now(),
            agent_id=self.id,
            new_position=new_position,
        )
        await self.world_socket_client.send_message(agent_new_position.json())

    async def agent_gets_world_objects_in_radius_action(self):
        agent_gets_world_objects_in_radius = AgentGetsWorldObjectsInRadiusEvent(
            created_at=datetime.now(),
            agent_id=self.id,
            current_agent_position=self.position,
            world_id=self.world_spawned_id,
            radius=self.vision_radius,
        )
        await self.world_socket_client.send_message(
            agent_gets_world_objects_in_radius.json()
        )

    async def agent_gets_world_agents_in_radius_action(self):
        agent_gets_world_agents_in_radius = AgentGetsWorldAgentsInRadiusEvent(
            created_at=datetime.now(),
            agent_id=self.id,
            position=self.position,
            radius=self.vision_radius,
        )
        await self.world_socket_client.send_message(
            agent_gets_world_agents_in_radius.json()
        )

    async def agent_gets_object_info_action(
        self,
        object_id: str,
    ):
        agent_gets_object_info = AgentGetsObjectInfoEvent(
            created_at=datetime.now(),
            agent_id=self.id,
            object_id=object_id,
        )
        await self.world_socket_client.send_message(agent_gets_object_info.json())

    async def agent_gets_agent_info_action(
        self,
        agent_id: str,
    ):
        agent_gets_agent_info = AgentGetsAgentInfoEvent(
            created_at=datetime.now(),
            agent_id=self.id,
            other_agent_id=agent_id,
        )
        await self.world_socket_client.send_message(agent_gets_agent_info.json())

    async def agent_interacts_with_object_action(
        self,
        created_interaction: str,
    ):
        await self.world_socket_client.send_message(created_interaction.json())

    async def agent_speaks_with_agent_action(
        self,
        other_agent_id: str,
        message: str,
    ):
        agent_speaks_with_agent = AgentSpeaksWithAgentEvent(
            created_at=datetime.now(),
            agent_id=self.id,
            other_agent_id=other_agent_id,
            message=message,
        )
        await self.world_socket_client.send_message(agent_speaks_with_agent.json())
