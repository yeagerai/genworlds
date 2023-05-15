from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from time import sleep
import json
from typing import List, Optional

from pydantic import ValidationError

from jsonschema import validate

import faiss
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from langchain.tools import StructuredTool
from langchain.tools.human.tool import HumanInputRun
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.llm import LLMChain
from langchain.schema import (
    AIMessage,
    BaseMessage,
    Document,
    HumanMessage,
    SystemMessage,
)

from yeager_core.agents.yeager_autogpt.output_parser import AutoGPTAction, AutoGPTOutputParser
from yeager_core.agents.yeager_autogpt.prompt import AutoGPTPrompt
from yeager_core.agents.yeager_autogpt.prompt_generator import FINISH_NAME
from yeager_core.sockets.world_socket_client import WorldSocketClient
from yeager_core.agents.yeager_autogpt.listening_antenna import ListeningAntenna
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.events.basic_events import (
    AgentGetsNearbyEntitiesEvent,
    AgentGetsObjectInfoEvent,
    AgentGetsAgentInfoEvent,
    AgentSpeaksWithAgentEvent,
    EntityRequestWorldStateUpdateEvent,
)


class YeagerAutoGPT:
    """Agent class for interacting with Auto-GPT."""

    # events: set = {AgentSpeaksWithAgentEvent}
    events: set = {}

    world_spawned_id: str

    def __init__(
        self,
        ai_name: str,
        description: str,
        goals: List[str],
        openai_api_key: str,
        feedback_tool: Optional[HumanInputRun] = None,
        additional_memories: Optional[List[VectorStoreRetriever]] = None,
        id: str = None,
    ):
        # Its own properties
        self.id = id if id else str(uuid4())
        self.ai_name = ai_name
        self.description = description
        self.goals = goals

        self.world_socket_client = WorldSocketClient(process_event=print)

        self.listening_antenna = ListeningAntenna(
            map(lambda e: e.__fields__['event_type'].default, self.events),
            agent_name=self.ai_name,
            agent_id=self.id,
        )

        # Agent actions
        self.actions = [
            # StructuredTool.from_function(
            #     name="agent_gets_nearby_entities_event",
            #     description="Gets nearby entities",
            #     func=self.agent_gets_nearby_entities_action,
            # ),
            # StructuredTool.from_function(
            #     name="get_object_info",
            #     description="Gets the info of an object.",
            #     func=self.agent_gets_object_info_action,
            # ),
            # StructuredTool.from_function(
            #     name="get_agent_info",
            #     description="Gets the info of an agent.",
            #     func=self.agent_gets_agent_info_action,
            # ),
            # StructuredTool.from_function(
            #     name="interact_with_object",
            #     description="Interacts with an object.",
            #     func=self.agent_interacts_with_object_action,
            # ),
        ]

        # Brain properties
        self.embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
        embedding_size = 1536
        index = faiss.IndexFlatL2(embedding_size)
        vectorstore = FAISS(
            self.embeddings_model.embed_query, index, InMemoryDocstore({}), {}
        )
        self.memory = vectorstore.as_retriever()

        llm = ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4")
        prompt = AutoGPTPrompt(
            ai_name=self.ai_name,
            ai_role=self.description,
            tools=self.actions,
            input_variables=["memory", "messages", "goals", "user_input", "nearby_entities", "relevant_commands", "plan", "agent_world_state"],
            token_counter=llm.get_num_tokens,
        )
        self.chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

        self.full_message_history: List[BaseMessage] = []
        self.next_action_count = 0
        self.output_parser = AutoGPTOutputParser()
        self.feedback_tool = None  # HumanInputRun() if human_in_the_loop else None
        self.schemas_memory : Chroma
        self.plan: Optional[str] = None

    def think(self):
        print(f" The agent {self.ai_name} is thinking...")
        user_input = (
            "Determine which next command to use, "
            "and respond using the format specified above:"
        )
        # Get the initial world state
        self.agent_request_world_state_update_action()

        sleep(10)
        # self.schemas_memory = Chroma.from_documents(self.listening_antenna.schemas_as_docs, self.embeddings_model)

        while True:
            agent_world_state = self.listening_antenna.get_agent_world_state()
             # if self.plan:
            #     # useful_schemas = self.schemas_memory.similarity_search(self.plan)
            # else:
            #     useful_schemas = [""]
            nearby_entities = self.listening_antenna.get_nearby_entities() # TODO: Vector similarity
            relevant_commands = []
            for entity in nearby_entities:
                entity_schemas = self.get_schemas()[entity["entity_class"]]
                
                for event_type, schema in entity_schemas.items():
                    description = schema['properties']['description']['default']

                    args = {}
                    for (property_name, property_details) in schema['properties'].items():
                        if property_name not in ['event_type', 'description', 'created_at', 'sender_id',]:
                            args[property_name] = property_details

                    # get_object_info: get_object_info(object_id: 'str') - Gets the info of an object., args json schema: {"object_id": {"title": "Object Id", "type": "string"}}
                    command = f"\"{entity['entity_class']}:{event_type}\" - {description}, args json schema: {json.dumps(args)}"
                    relevant_commands.append(command)

            # Add world
            entity_class = "World"
            entity_schemas = self.get_schemas()[entity_class]
                
            for event_type, schema in entity_schemas.items():
                if (event_type in self.listening_antenna.special_events):
                    continue
                
                description = schema['properties']['description']['default']

                args = {}
                for (property_name, property_details) in schema['properties'].items():
                    if property_name not in ['event_type', 'description', 'created_at', 'sender_id',]:
                        args[property_name] = property_details
                        # args_string += f"{property_name}: {property_details['type']}, "

                # get_object_info: get_object_info(object_id: 'str') - Gets the info of an object., args json schema: {"object_id": {"title": "Object Id", "type": "string"}}
                command = f"\"{entity_class}:{event_type}\" - {description}, args json schema: {json.dumps(args)}"
                relevant_commands.append(command)


            # Send message to AI, get response
            assistant_reply = self.chain.run(
                goals=self.goals,
                messages=self.full_message_history,
                memory=self.memory,
                nearby_entities=nearby_entities,
                relevant_commands=relevant_commands,
                plan=self.plan,
                user_input=user_input,
                agent_world_state=agent_world_state,
            )
            self.plan = json.loads(assistant_reply)["thoughts"]["plan"]
            # Print Assistant thoughts
            print(assistant_reply) # Send the thoughts as events
            self.full_message_history.append(HumanMessage(content=user_input))
            self.full_message_history.append(AIMessage(content=assistant_reply))

            # Get command name and arguments
            actions = self.output_parser.parse(assistant_reply)
            result = ""
            for action in actions:
                tools = {t.name: t for t in self.actions}
                if action.name == FINISH_NAME:
                    return action.args["response"]
                elif action.name == "ERROR":
                    result += f"Error: {action.args}. \n"
                elif action.name in tools:
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
                    result += f"Command {tool.name} returned: {observation} \n"
                else:
                    result += self.execute_event_action(action) + "\n"	

                
            ## send result and assistant_reply to the socket
            print(result)

            # If there are any relevant events in the world for this agent, add them to memory
            sleep(3)
            last_events = self.listening_antenna.get_last_events()
            memory_to_add = (
                f"Assistant Reply: {assistant_reply} "
                f"\nResult: {result} "
                f"\nLast World Events: {last_events}"
            )

            print(f"Adding to memory: {memory_to_add}")

            if self.feedback_tool is not None:
                feedback = f"\n{self.feedback_tool.run('Input: ')}"
                if feedback in {"q", "stop"}:
                    print("EXITING")
                    return "EXITING"
                memory_to_add += feedback

            self.memory.add_documents([Document(page_content=memory_to_add)])
            self.full_message_history.append(SystemMessage(content=result))

    def get_agent_world_state(self):
        return self.listening_antenna.get_agent_world_state()
    
    def get_nearby_entities(self):
        return self.listening_antenna.get_nearby_entities()
    
    def get_schemas(self):
        return self.listening_antenna.get_schemas()


    def execute_event_action(self, action: AutoGPTAction):
        try:
            class_name = action.name.split(":")[0]
            event_type = action.name.split(":")[1] 

            event = {
                "event_type": event_type,
                "sender_id": self.id,	
                "created_at": datetime.now().isoformat(),
            }
            event.update(action.args)

            print(event)

            event_schema = self.get_schemas()[class_name][event_type]
            validate(event, event_schema)

            self.world_socket_client.send_message(json.dumps(event))
            return f"Action {action.name} sent to the world."
        except IndexError as e:
            return (
                f"Unknown command '{action.name}'. "
                f"Please refer to the 'COMMANDS' list for available "
                f"commands and only respond in the specified JSON format."
            )
        except ValidationError as e:
            return (
                f"Validation Error in args: {str(e)}, args: {action.args}"
            )
        except Exception as e:
            return (
                f"Error: {str(e)}, {type(e).__name__}, args: {action.args}"
            )


    def agent_gets_nearby_entities_action(self):
        agent_gets_nearby_entities_event = AgentGetsNearbyEntitiesEvent(
            created_at=datetime.now(),
            sender_id=self.id,
        )
        self.world_socket_client.send_message(agent_gets_nearby_entities_event.json())

    def agent_gets_object_info_action(
        self,
        target_id: str,
    ):
        agent_gets_object_info = AgentGetsObjectInfoEvent(
            created_at=datetime.now(),
            sender_id=self.id,
            target_id=target_id,
        )
        self.world_socket_client.send_message(agent_gets_object_info.json())

    def agent_gets_agent_info_action(
        self,
        target_id: str,
    ):
        agent_gets_agent_info = AgentGetsAgentInfoEvent(
            created_at=datetime.now(),
            sender_id=self.id,
            target_id=target_id,
        )
        self.world_socket_client.send_message(agent_gets_agent_info.json())

    def agent_interacts_with_object_action(
        self,
        created_interaction: str,
    ):
        self.world_socket_client.send_message(created_interaction)

    def agent_speaks_with_agent_action(
        self,
        target_id: str,
        message: str,
    ):
        agent_speaks_with_agent = AgentSpeaksWithAgentEvent(
            created_at=datetime.now(),
            sender_id=self.id,
            target_id=target_id,
            message=message,
        )
        self.world_socket_client.send_message(agent_speaks_with_agent.json())

    def agent_request_world_state_update_action(self):
        agent_request_world_state_update = EntityRequestWorldStateUpdateEvent(
            created_at=datetime.now(),
            sender_id=self.id,
            target_id=self.world_spawned_id,
        )
        self.world_socket_client.send_message(agent_request_world_state_update.json())
