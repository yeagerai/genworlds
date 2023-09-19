from __future__ import annotations

from datetime import datetime
import threading
from uuid import uuid4
from time import sleep
import json
from typing import List, Optional, Dict, Any
from pydantic import ValidationError, create_model
from jsonschema import validate

from langchain.tools.human.tool import HumanInputRun
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import (
    AIMessage,
    BaseMessage,
    SystemMessage,
)
from qdrant_client import QdrantClient

from genworlds.events.base_event import BaseEvent
from genworlds.agents.base_agent.thoughts.thought import Thought
from genworlds.worlds.base_world.events import (
    EntityRequestWorldStateUpdateEvent,
    AgentSpeaksWithUserEvent,
    WorldSendsSchemasEvent,
    EntityWorldStateUpdateEvent,
    WorldSendsAllEntitiesEvent,
)
from genworlds.utils.logging_factory import LoggingFactory
from genworlds.objects.base_object.base_object import BaseObject
from genworlds.agents.base_agent.memories.simulation_memory import SimulationMemory

FINISH_NAME = "finish"


class BaseAgent(BaseObject):
    """
    Base GenWorlds Agent class.
    """

    world_spawned_id: str
    personality_db = None
    agent_world_state = "You have not yet learned about the world state."

    def __init__(
        self,
        name: str,
        description: str,
        goals: List[str],
        openai_api_key: str,
        navigation_thought: Thought,
        execution_thoughts: dict[str, Thought],
        action_thought_map: dict,
        important_event_types: set[str],
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
        self.name = name
        self.description = description
        self.goals = goals
        self.feedback_tool = feedback_tool

        # Start/Stop properties
        self.interesting_events = interesting_events
        self.wakeup_events = wakeup_events
        self.can_sleep = can_sleep
        self.is_asleep = False

        # Listener properties
        self.special_events = {
            "world_sends_schemas_event",
            "entity_world_state_update_event",
            "world_sends_all_entities_event",
        }
        self.non_memory_important_event_types = {
            "world_sends_schemas_event",
            "entity_world_state_update_event",
            "world_sends_all_entities_event",
        }
        self.schemas = {}
        self.all_entities = []
        self.all_events = []
        self.last_events = []

        self.important_event_types = self.special_events.copy()
        self.important_event_types.update(important_event_types)

        # Logger
        self.logger = LoggingFactory.get_logger(self.name)

        # Agent actions
        self.actions = []

        # Thought properties
        self.navigation_thought = navigation_thought
        self.execution_thoughts = execution_thoughts
        self.action_thought_map = action_thought_map

        self.full_message_history: List[BaseMessage] = []
        self.next_action_count = 0
        self.feedback_tool = None  # HumanInputRun() if human_in_the_loop else None
        self.plan: Optional[str] = None

        # Memories
        self.additional_memories = additional_memories
        self.simulation_memory = SimulationMemory(
            openai_api_key=openai_api_key,
            n_of_last_events=10,
            n_of_similar_events=0,
            n_of_paragraphs_in_summary=3,
        )
        self.schemas_memory: Qdrant
        self.embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.personality_db_qdrant_client = personality_db_qdrant_client
        if self.personality_db_qdrant_client:
            self.personality_db = Qdrant(
                collection_name=personality_db_collection_name,
                embeddings=self.embeddings_model,
                client=self.personality_db_qdrant_client,
            )

        super().__init__(
            id=self.id,
            name=self.name,
            description=self.description,
            websocket_url=websocket_url,
        )
        self.register_event_listeners(
            [
                [WorldSendsSchemasEvent, self.update_schemas],
                [EntityWorldStateUpdateEvent, self.update_world_state],
                [WorldSendsAllEntitiesEvent, self.update_all_entities],
                [BaseEvent, self.listen_for_events],
            ]
        )
        self.register_event_classes(
            [EntityRequestWorldStateUpdateEvent, AgentSpeaksWithUserEvent]
        )

    def think(self):
        self.logger.info(f" The agent {self.name} is thinking...")
        user_input = (
            "Determine which next command to use, "
            "and respond using the format specified above:"
        )
        # Get the initial world state
        self.agent_request_world_state_update_action()

        next_actions = []

        sleep(5)

        while True:
            # If there are any relevant events in the world for this agent, add them to memory
            last_events = self.get_last_events()
            self.logger.debug(f"Last events: {last_events}")
            for event in last_events:
                self.simulation_memory.add_event(event.json(), summarize=True)
                self.handle_wakeup(event)

            if self.is_asleep:
                self.logger.info(f"Sleeping...")
                sleep(5)
                continue

            agent_world_state = self.get_agent_world_state()
            all_entities = self.get_all_entities()

            if len(all_entities) > 0:
                all_entities_store = Qdrant.from_texts(
                    list(map(json.dumps, all_entities.values())),
                    self.embeddings_model,
                    location=":memory:",
                )

                if self.plan:
                    useful_all_entities = all_entities_store.similarity_search(
                        str(self.plan)
                    )
                else:
                    useful_all_entities = all_entities_store.similarity_search(
                        json.dumps(self.goals)
                    )

                useful_all_entities = list(
                    map(lambda d: json.loads(d.page_content), useful_all_entities)
                )
            else:
                useful_all_entities = []

            relevant_commands = {
                # Default commands
                "Self:wait": {
                    "title": "Self:wait",
                    "description": "Wait until the state of the world changes",
                    "args": {},
                    "string_short": "Self:wait - Wait until the state of the world changes",
                    "string_full": "Self:wait - Wait until the state of the world changes, args json schema: {}",
                },
                "Self:agent_speaks_with_user_event": {
                    "title": "Self:agent_speaks_with_user_event",
                    "description": "Respond to a question from the user",
                    "args": {
                        "message": {
                            "title": "message",
                            "description": "The message sent by the agent to the user",
                            "type": "string",
                        },
                        "target_id": {
                            "title": "Target Id",
                            "description": "ID of the entity that handles the event",
                            "type": "string",
                        },
                    },  # response, target_user
                    "string_short": "Self:agent_speaks_with_user_event - Respond to a question from the user",
                    "string_full": 'Self:agent_speaks_with_user_event - Respond to a question from the user, args json schema: {"message":{"title":"message", "description":"The message sent by the agent to the user","type":"string"}, "target_id": {"title": "Target Id", "description": "ID of the entity that handles the event", "type": "string"}}',  # response, target_user
                },
            }
            for entity in useful_all_entities:
                entity_schemas = self.get_schemas()[entity["entity_class"]]
                for event_type, schema in entity_schemas.items():
                    description = schema["properties"]["description"]

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

            if len(next_actions) > 0:
                filtered_relevant_commands = {
                    cmd: info
                    for cmd, info in relevant_commands.items()
                    if cmd == "Self:wait"
                    or cmd == "Self:agent_speaks_with_user_event"
                    or cmd == next_actions[0]
                }

                relevant_commands = filtered_relevant_commands
                next_actions = next_actions[1:]

            # Add world
            entity_class = "World"
            entity_schemas = self.get_schemas()[entity_class]

            for event_type, schema in entity_schemas.items():
                if event_type in self.special_events:
                    continue

                description = schema["properties"]["description"]

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
            navigation_plan_parsed = self.navigation_thought.run(
                {
                    "goals": self.goals,
                    "messages": self.full_message_history,
                    "memory": self.simulation_memory,
                    "personality_db": self.personality_db,
                    "all_entities": list(
                        filter(
                            lambda e: (e["held_by"] != self.id),
                            self.all_entities.values(),
                        )
                    ),
                    "inventory": list(
                        filter(
                            lambda e: (e["held_by"] == self.id),
                            self.all_entities.values(),
                        )
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

                if selected_action in self.action_thought_map:
                    action_brains = self.action_thought_map[selected_action]["brains"]
                    if len(next_actions) == 0:
                        next_actions = self.action_thought_map[selected_action][
                            "next_actions"
                        ]
                else:
                    action_brains = self.action_thought_map["default"]["brains"]
                    if len(next_actions) == 0:
                        next_actions = self.action_thought_map["default"][
                            "next_actions"
                        ]

                previous_brain_outputs = [
                    f"Current goal: {action_goal_description}",
                ]
                for action_brain_name in action_brains:
                    action_brain = self.execution_thoughts[action_brain_name]

                    previous_brain_outputs.append(
                        action_brain.run(
                            {
                                "goals": self.goals,
                                "messages": self.full_message_history,
                                "memory": self.simulation_memory,
                                "personality_db": self.personality_db,
                                "all_entities": list(
                                    filter(
                                        lambda e: (e["held_by"] != self.id),
                                        all_entities,
                                    )
                                ),
                                "inventory": list(
                                    filter(
                                        lambda e: (e["held_by"] == self.id),
                                        all_entities,
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
                        self.simulation_memory.add_event(
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

            if len(next_actions) > 0:
                self.logger.info(
                    f"Inside a deterministic chain... Changing plan for navigatior brain: (Self:wait, {next_actions[0]})"
                )

            ## send result and assistant_reply to the socket
            self.logger.info(result)

            self.full_message_history.append(SystemMessage(content=result))

            # Allow events to be processed
            sleep(3)

    def get_schemas(self):
        events = {}
        events["agent_speaks_with_user_event"] = AgentSpeaksWithUserEvent.schema()
        self.schemas["Self"] = events
        return self.schemas

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
            summary = self.simulation_memory.one_line_summarizer.summarize(
                json.dumps(event)
            )
            event["summary"] = summary
            self.logger.debug(event)

            event_schema = self.get_schemas()[class_name][event_type]
            validate(event, event_schema)

            self.send_event(json.dumps(event))
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
        self.send_event(
            EntityRequestWorldStateUpdateEvent,
            target_id=self.world_spawned_id,
        )

    def add_wakeup_event(self, event_class: BaseEvent, params: dict):
        self.wakeup_events[event_class.__fields__["event_type"].default] = params
        self.register_event_listener(event_class, self.handle_wakeup)

    def handle_wakeup(self, event):
        event_type = event.event_type
        if event_type not in self.wakeup_events:
            return

        wakeup_event_property_filters = self.wakeup_events[event_type]

        # Check if the event matches the filters
        is_match = True
        for (
            wakeup_event_property,
            expected_value,
        ) in wakeup_event_property_filters.items():
            # Use getattr to dynamically access event attributes using their string names
            actual_value = getattr(event, wakeup_event_property, None)
            if actual_value != expected_value:
                is_match = False
                break

        if is_match:
            self.logger.info("Waking up ...")
            self.is_asleep = False

    def launch_threads(self):
        self.launch_websocket_thread()
        sleep(0.1)
        threading.Thread(
            target=self.think,
            name=f"Agent {self.name} Thinking Thread",
            daemon=True,
        ).start()
        self.logger.info("Threads launched")

    def update_schemas(self, event: WorldSendsSchemasEvent):
        self.schemas = event.schemas
        self.update_event_classes_from_new_schemas(event.schemas)

    def json_schema_to_pydantic_model(self, schema: Dict[str, Any]) -> Any:
        name = schema.get("title", "DynamicModel")
        fields = {
            k: (v.get("type"), v.get("default"))
            for k, v in schema["properties"].items()
        }
        return create_model(name, **fields)

    def update_event_classes_from_new_schemas(self, schemas):
        for entity in schemas:
            for event in schemas[entity]:
                Model = self.json_schema_to_pydantic_model(schemas[entity][event])
                event_type = Model.__fields__["event_type"].default
                if event_type not in self.event_classes:
                    self.event_classes[event_type] = Model

    def update_world_state(self, event: EntityWorldStateUpdateEvent):
        if event.target_id == self.id:
            self.agent_world_state = event.entity_world_state

    def update_all_entities(self, event: WorldSendsAllEntitiesEvent):
        self.all_entities = event.all_entities

    def listen_for_events(self, event: BaseEvent):
        if (
            event.sender_id != self.id
            and (
                event.target_id == self.id
                or event.event_type in self.important_event_types
            )
            and event.event_type not in self.non_memory_important_event_types
        ):
            self.last_events.append(event)
            self.all_events.append(event)

    def get_last_events(self):
        events_to_return = self.last_events.copy()
        self.last_events = []
        return events_to_return

    def get_all_events(self):
        return self.all_events

    def get_agent_world_state(self):
        return self.agent_world_state

    def get_all_entities(self):
        return self.all_entities
