from __future__ import annotations

from datetime import datetime
import threading
from uuid import uuid4
from time import sleep
import json
from typing import List, Optional

from pydantic import ValidationError
from jsonschema import validate

from langchain.tools import StructuredTool
from langchain.tools.human.tool import HumanInputRun
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import (
    AIMessage,
    BaseMessage,
    Document,
    HumanMessage,
    SystemMessage,
)
from qdrant_client import QdrantClient
from genworlds.agents.tree_agent.brains.brain import Brain

from genworlds.events.basic_events import (
    EntityRequestWorldStateUpdateEvent,
)
from genworlds.utils.logging_factory import LoggingFactory

from genworlds.sockets.world_socket_client import WorldSocketClient
from genworlds.agents.world_listeners.listening_antenna import ListeningAntenna
from genworlds.agents.memory_processors.nmk_world_memory import NMKWorldMemory

FINISH_NAME = "finish"


class TreeAgent:
    """Agent class for structured tree-of-thought execution."""

    world_spawned_id: str
    personality_db = None

    def __init__(
        self,
        ai_name: str,
        description: str,
        goals: List[str],
        openai_api_key: str,
        navigation_brain: Brain,
        execution_brains: dict[str, Brain],
        action_brain_map: dict,
        interesting_events: set = {},
        can_sleep: bool = True,
        wakeup_events: dict = {},
        feedback_tool: Optional[HumanInputRun] = None,
        additional_memories: Optional[List[VectorStoreRetriever]] = None,
        id: str = None,
        personality_db_qdrant_client: QdrantClient = None,
        personality_db_collection_name: str = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        # Its own properties
        self.id = id if id else str(uuid4())
        self.ai_name = ai_name
        self.description = description
        self.goals = goals
        self.interesting_events = interesting_events
        self.can_sleep = can_sleep
        self.wakeup_events = wakeup_events
        self.feedback_tool = feedback_tool
        self.additional_memories = additional_memories

        self.is_asleep = False

        self.logger = LoggingFactory.get_logger(self.ai_name)

        self.world_socket_client = WorldSocketClient(
            process_event=None, url=websocket_url
        )

        self.listening_antenna = ListeningAntenna(
            self.interesting_events,
            agent_name=self.ai_name,
            agent_id=self.id,
            websocket_url=websocket_url,
        )

        # Agent actions
        self.actions = []

        # Brain properties
        self.nmk_world_memory = NMKWorldMemory(
            openai_api_key=openai_api_key,
            n_of_last_events=10,
            n_of_similar_events=0,
            n_of_paragraphs_in_summary=3,
        )

        self.navigation_brain = navigation_brain
        self.execution_brains = execution_brains
        self.action_brain_map = action_brain_map

        self.full_message_history: List[BaseMessage] = []
        self.next_action_count = 0
        self.feedback_tool = None  # HumanInputRun() if human_in_the_loop else None
        self.schemas_memory: Qdrant
        self.plan: Optional[str] = None

        self.embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.personality_db_qdrant_client = personality_db_qdrant_client
        if self.personality_db_qdrant_client:
            self.personality_db = Qdrant(
                collection_name=personality_db_collection_name,
                embeddings=self.embeddings_model,
                client=self.personality_db_qdrant_client,
            )
            
    def think(self):
        self.logger.info(f" The agent {self.ai_name} is thinking...")
        user_input = (
            "Determine which next command to use, "
            "and respond using the format specified above:"
        )
        # Get the initial world state
        self.agent_request_world_state_update_action()

        sleep(5)

        while True:
            # If there are any relevant events in the world for this agent, add them to memory
            last_events = self.listening_antenna.get_last_events()
            self.logger.debug(f"Last events: {last_events}")
            for event in last_events:
                self.nmk_world_memory.add_event(json.dumps(event), summarize=True)
                self.handle_wakeup(event)

            if self.is_asleep:
                self.logger.info(f"Sleeping...")
                sleep(5)
                continue

            agent_world_state = self.listening_antenna.get_agent_world_state()
            nearby_entities = self.listening_antenna.get_nearby_entities()

            if len(nearby_entities) > 0:
                nearby_entities_store = Qdrant.from_texts(
                    list(map(json.dumps, nearby_entities)),
                    self.embeddings_model,
                    location=":memory:",
                )

                if self.plan:
                    useful_nearby_entities = nearby_entities_store.similarity_search(
                        str(self.plan)
                    )
                else:
                    useful_nearby_entities = nearby_entities_store.similarity_search(
                        json.dumps(self.goals)
                    )

                useful_nearby_entities = list(
                    map(lambda d: json.loads(d.page_content), useful_nearby_entities)
                )
            else:
                useful_nearby_entities = []

            relevant_commands = {
                # Default commands
                "Self:wait": {
                    "title": "Self:wait",
                    "description": "Wait until the state of the world changes",
                    "args": {},
                    "string_short": "Self:wait - Wait until the state of the world changes",
                    "string_full": "Self:wait - Wait until the state of the world changes, args json schema: {}",
                },
            }
            for entity in useful_nearby_entities:
                entity_schemas = self.get_schemas()[entity["entity_class"]]

                for event_type, schema in entity_schemas.items():
                    description = schema["properties"]["description"]["default"]

                    args = {}
                    for property_name, property_details in schema["properties"].items():
                        if property_name not in [
                            "event_type",
                            "description",
                            "created_at",
                            "sender_id",
                            "summary",
                        ]:
                            args[property_name] = property_details

                    selected_command = {
                        "title": f"{entity['entity_class']}:{event_type}",
                        "description": description,
                        "args": args,
                        "string_short": f"{entity['entity_class']}:{event_type} - {description}",
                        "string_full": f"\"{entity['entity_class']}:{event_type}\" - {description}, args json schema: {json.dumps(args)}",
                    }
                    relevant_commands[selected_command["title"]] = selected_command

            # Add world
            entity_class = "World"
            entity_schemas = self.get_schemas()[entity_class]

            for event_type, schema in entity_schemas.items():
                if event_type in self.listening_antenna.special_events:
                    continue

                description = schema["properties"]["description"]["default"]

                args = {}
                for property_name, property_details in schema["properties"].items():
                    if property_name not in [
                        "event_type",
                        "description",
                        "created_at",
                        "sender_id",
                        "summary",
                    ]:
                        args[property_name] = property_details

                selected_command = {
                    "title": f"{entity_class}:{event_type}",
                    "description": description,
                    "args": args,
                    "string_short": f"{entity_class}:{event_type} - {description}",
                    "string_full": f'"{entity_class}:{event_type}" - {description}, args json schema: {json.dumps(args)}',
                }
                relevant_commands[selected_command["title"]] = selected_command

            # Send message to AI, get response
            navigation_plan_parsed = self.navigation_brain.run(
                {
                    "goals": self.goals,
                    "messages": self.full_message_history,
                    "memory": self.nmk_world_memory,
                    "personality_db": self.personality_db,
                    "nearby_entities": list(
                        filter(lambda e: (e["held_by"] != self.id), nearby_entities)
                    ),
                    "inventory": list(
                        filter(lambda e: (e["held_by"] == self.id), nearby_entities)
                    ),
                    "plan": self.plan,
                    "user_input": user_input,
                    "agent_world_state": agent_world_state,
                    "relevant_commands": relevant_commands,
                }
            )

            # Print Assistant thoughts
            self.logger.info(navigation_plan_parsed)
            self.full_message_history.append(
                AIMessage(content=str(navigation_plan_parsed))
            )

            self.plan = navigation_plan_parsed["plan"]

            selected_action = navigation_plan_parsed["next_action"]
            action_goal_description = navigation_plan_parsed["next_action_aim"]

            result = ""
            event_sent_summary = ""
            if selected_action == "Self:exit":
                self.logger.info(f"Exiting...")
                return "FINISHED"
            elif selected_action == "Self:wait":
                self.logger.info(f"Waiting, entering sleep mode...")
                if self.can_sleep:
                    self.is_asleep = True
                else:
                    sleep(10)
                result += f"Waiting...\n"
            # TODO: tools?
            elif selected_action in relevant_commands:
                selected_command = relevant_commands[selected_action]

                if selected_action in self.action_brain_map:
                    action_brains = self.action_brain_map[selected_action]
                else:
                    action_brains = self.action_brain_map["default"]

                previous_brain_outputs = [
                    f"Current goal: {action_goal_description}",
                ]
                for action_brain_name in action_brains:
                    action_brain = self.execution_brains[action_brain_name]

                    previous_brain_outputs.append(
                        action_brain.run(
                            {
                                "goals": self.goals,
                                "messages": self.full_message_history,
                                "memory": self.nmk_world_memory,
                                "personality_db": self.personality_db,
                                "nearby_entities": list(
                                    filter(
                                        lambda e: (e["held_by"] != self.id),
                                        nearby_entities,
                                    )
                                ),
                                "inventory": list(
                                    filter(
                                        lambda e: (e["held_by"] == self.id),
                                        nearby_entities,
                                    )
                                ),
                                "plan": self.plan,
                                "user_input": user_input,
                                "agent_world_state": agent_world_state,
                                "command_to_execute": selected_command,
                                "previous_brain_outputs": previous_brain_outputs,
                            }
                        )
                    )
                final_brain_output = previous_brain_outputs[-1]
                try:
                    args = final_brain_output

                    if type(args) == dict:
                        event_sent = self.execute_event_with_args(
                            selected_command["title"], args
                        )
                        self.nmk_world_memory.add_event(
                            json.dumps(event_sent), summarize=True
                        )
                        event_sent_summary += (
                            "Event at: " + event_sent["created_at"] + "\n"
                        )
                        event_sent_summary += (
                            "What happened: " + str(event_sent["summary"]) + "\n"
                        )

                        result += event_sent_summary
                    else:
                        raise Exception("Unexpected final output")

                except Exception as e:
                    self.logger.error(
                        f"Problem executing command with {selected_command['title']} with output {final_brain_output}: {e}\n"
                    )
                    result += f"Problem executing command with {selected_command['title']} with output {final_brain_output}: {e}\n"
            else:
                self.logger.info(f"Invalid command: {selected_action}")
                result += f"Error: {selected_action} is not recognized. \n"
                continue

            ## send result and assistant_reply to the socket
            self.logger.info(result)

            self.full_message_history.append(SystemMessage(content=result))

            # Allow events to be processed
            sleep(3)

    def get_agent_world_state(self):
        return self.listening_antenna.get_agent_world_state()

    def get_nearby_entities(self):
        return self.listening_antenna.get_nearby_entities()

    def get_schemas(self):
        return self.listening_antenna.get_schemas()

    def execute_event_with_args(self, name: str, args: dict):
        try:
            class_name = name.split(":")[0]
            event_type = name.split(":")[1]

            event = {
                "event_type": event_type,
                "sender_id": self.id,
                "created_at": datetime.now().isoformat(),
            }
            event.update(args)
            summary = self.nmk_world_memory.one_line_summarizer.summarize(
                json.dumps(event)
            )
            event["summary"] = summary
            self.logger.debug(event)

            event_schema = self.get_schemas()[class_name][event_type]
            validate(event, event_schema)

            self.world_socket_client.send_message(json.dumps(event))
            return event
        except IndexError as e:
            return (
                f"Unknown command '{name}'. "
                f"Please refer to the 'COMMANDS' list for available "
                f"commands and only respond in the specified JSON format."
            )
        except ValidationError as e:
            return f"Validation Error in args: {str(e)}, args: {args}"
        except Exception as e:
            return f"Error: {str(e)}, {type(e).__name__}, args: {args}"

    def agent_request_world_state_update_action(self):
        agent_request_world_state_update = EntityRequestWorldStateUpdateEvent(
            created_at=datetime.now(),
            sender_id=self.id,
            target_id=self.world_spawned_id,
        )
        self.world_socket_client.send_message(agent_request_world_state_update.json())

    def handle_wakeup(self, event):
        event_type = event["event_type"]
        if event_type not in self.wakeup_events:
            return

        wakeup_event_property_filters = self.wakeup_events[event_type]

        # Check if the event matches the filters
        is_match = True
        for wakeup_event_property in wakeup_event_property_filters.keys():
            expected_value = wakeup_event_property_filters[wakeup_event_property]
            if event[wakeup_event_property] != expected_value:
                is_match = False
                break

        if is_match:
            self.logger.info("Waking up", event)
            self.is_asleep = False

    def launch_threads(self):
        threading.Thread(
            target=self.listening_antenna.world_socket_client.websocket.run_forever,
            name=f"Agent {self.ai_name} Listening Thread",
            daemon=True,
        ).start()
        sleep(0.1)
        threading.Thread(
            target=self.world_socket_client.websocket.run_forever,
            name=f"Agent {self.ai_name} Speaking Thread",
            daemon=True,
        ).start()
        sleep(0.1)
        threading.Thread(
            target=self.think,
            name=f"Agent {self.ai_name} Thinking Thread",
            daemon=True,
        ).start()
        self.logger.info("Threads launched")
