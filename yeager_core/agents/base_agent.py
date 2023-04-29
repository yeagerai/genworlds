from uuid import uuid4
from typing import List

import faiss
from langchain.experimental import AutoGPT
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.embeddings import OpenAIEmbeddings
from langchain.agents import Tool

from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.sockets.world_socket_client import WorldSocketClient
from yeager_core.events.base_event import EventHandler, EventDict, Listener

class BaseAgent:
    def __init__(
        self,
        name: str,
        description: str,
        goals: List[str],
        position: Coordinates,
        size: Size,
        event_dict: EventDict,
        event_handler: EventHandler,
        important_event_types: List[str],
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
        self.name = name
        self.description = description
        self.goals = goals
        self.position = position
        self.size = size
        self.world_socket_client = WorldSocketClient()

        self.actions = [
            # The tools should be the basic actions that the agent can do to interact with agents and objects
            Tool(
            name="move",
            description="Moves the agent to a position.",
            func=self.move,# does whatever process and triggers an event to the socket
            ),
        ]

        # Define your embedding model
        embeddings_model = OpenAIEmbeddings()
        # Initialize the vectorstore as empty

        embedding_size = 1536
        index = faiss.IndexFlatL2(embedding_size)
        vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})

        self.brain = AutoGPT.from_llm_and_tools(
            ai_name=self.name,
            ai_role=self.description,
            tools=self.actions,
            llm=ChatOpenAI(),
            memory=vectorstore.as_retriever()
        )

    async def attach_to_world(self):
        # this is the autopilot mode
        with self.world_socket_client.ws_connection as websocket:
            while True:
                trigger_event = await websocket.recv()
                if trigger_event["event_type"] in self.important_event_types:
