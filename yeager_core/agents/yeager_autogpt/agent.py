from __future__ import annotations
from uuid import uuid4
from typing import List, Optional

from pydantic import ValidationError
import asyncio

from langchain.chains.llm import LLMChain
from langchain.chat_models.base import BaseChatModel
from yeager_core.agents.yeager_autogpt.output_parser import (
    AutoGPTOutputParser,
    BaseAutoGPTOutputParser,
)
from yeager_core.agents.yeager_autogpt.prompt import AutoGPTPrompt
from yeager_core.agents.yeager_autogpt.prompt_generator import (
    FINISH_NAME,
)
from langchain.schema import (
    AIMessage,
    BaseMessage,
    Document,
    HumanMessage,
    SystemMessage,
)
from langchain.tools.base import BaseTool
from langchain.tools.human.tool import HumanInputRun
from langchain.vectorstores.base import VectorStoreRetriever

from yeager_core.sockets.world_socket_client import WorldSocketClient
from yeager_core.agents.yeager_autogpt.listening_antena import ListeningAntena
from yeager_core.events.base_event import EventHandler, EventDict
from yeager_core.properties.basic_properties import Coordinates, Size
class YeagerAutoGPT:
    """Agent class for interacting with Auto-GPT."""

    def __init__(
        self,
        ai_name: str,
        memory: VectorStoreRetriever,
        chain: LLMChain,
        output_parser: BaseAutoGPTOutputParser,
        tools: List[BaseTool],
        position: Coordinates,
        size: Size,
        event_dict: EventDict,
        event_handler: EventHandler,
        important_event_types: List[str],
        goals: List[str],
        feedback_tool: Optional[HumanInputRun] = None,

    ):
        self.important_event_types = important_event_types
        important_event_types.extend(
            [
                "agent_move_to_position",

                "agent_gets_world_objects_in_radius",
                "agent_gets_world_agents_in_radius",

                "agent_gets_object_info", # retrieves the possible interactions
                "agent_gets_agent_info", # by now the only possible interaction is having a conversation

                "agent_interacts_with_object", # thinks about which interaction to do and prepares the event and sends it to the ws
                "agent_interacts_with_agent",
            ]
        )

        self.event_dict = event_dict

        self.id = uuid4()

        self.ai_name = ai_name
        self.goals = goals
        self.memory = memory
        self.full_message_history: List[BaseMessage] = []
        self.next_action_count = 0
        self.vision_radius = 50
        self.chain = chain
        self.output_parser = output_parser
        self.tools = tools
        self.feedback_tool = feedback_tool
        self.position = position
        self.size = size
        self.world_socket_client = WorldSocketClient()
        self.listening_antena = ListeningAntena(self.world_socket_client, self.important_event_types)

    @classmethod
    def from_llm_and_tools(
        cls,
        ai_name: str,
        ai_role: str,
        memory: VectorStoreRetriever,
        tools: List[BaseTool],
        llm: BaseChatModel,
        human_in_the_loop: bool = False,
        output_parser: Optional[BaseAutoGPTOutputParser] = None,
    ) -> YeagerAutoGPT:
        prompt = AutoGPTPrompt(
            ai_name=ai_name,
            ai_role=ai_role,
            tools=tools,
            input_variables=["memory", "messages", "goals", "user_input"],
            token_counter=llm.get_num_tokens,
        )
        human_feedback_tool = HumanInputRun() if human_in_the_loop else None
        chain = LLMChain(llm=llm, prompt=prompt)
        return cls(
            ai_name,
            memory,
            chain,
            output_parser or AutoGPTOutputParser(),
            tools,
            feedback_tool=human_feedback_tool,
        )


    def attach_to_world(self):
        asyncio.run(self.listening_antena.listen())
        asyncio.run(self.think())

    def think(self):
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
            tools = {t.name: t for t in self.tools}
            if action.name == FINISH_NAME:
                return action.args["response"]
            if action.name in tools:
                tool = tools[action.name]
                try:
                    observation = tool.run(action.args)
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
            last_events = self.listening_antena.get_last_events()
            memory_to_add = (
                f"Assistant Reply: {assistant_reply} " f"\nResult: {result} " f"\nLast World Events: {last_events}"
            )

            if self.feedback_tool is not None:
                feedback = f"\n{self.feedback_tool.run('Input: ')}"
                if feedback in {"q", "stop"}:
                    print("EXITING")
                    return "EXITING"
                memory_to_add += feedback

            self.memory.add_documents([Document(page_content=memory_to_add)])
            self.full_message_history.append(SystemMessage(content=result))

    async def agent_move_to_position(self, new_position: Coordinates):
        agent_new_position = AgentMoveToPosition(
            agent_id=self.id,
            new_position=new_position,
        )
        await self.world_socket_client.send_message(agent_new_position.json())

    async def agent_gets_world_objects_in_radius(
        self
    ):
        agent_gets_world_objects_in_radius = AgentGetsWorldObjectsInRadius(
            agent_id=self.id,
            position=self.position,
            radius=self.vision_radius,
        )
        await self.world_socket_client.send_message(agent_gets_world_objects_in_radius.json())

    async def agent_gets_world_agents_in_radius(
        self
    ):
        agent_gets_world_agents_in_radius = AgentGetsWorldAgentsInRadius(
            agent_id=self.id,
            position=self.position,
            radius=self.vision_radius,
        )
        await self.world_socket_client.send_message(agent_gets_world_agents_in_radius.json())
