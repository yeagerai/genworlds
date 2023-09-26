from __future__ import annotations

from abc import ABC, abstractmethod
import threading
from uuid import uuid4
from time import sleep
import json
from typing import List, Optional

from langchain.vectorstores import Qdrant
from langchain.schema import (
    AIMessage,
    BaseMessage,
    SystemMessage,
)
from genworlds.agents.base_agent.action_planner import (
    ActionPlanner,
    AbstractActionPlanner,
)
from genworlds.agents.base_agent.action_validator import (
    ActionValidator,
    AbstractActionValidator,
)
from genworlds.agents.base_agent.state_manager import StateManager, AbstractStateManager
from genworlds.simulation.sockets.handlers.event_handler import (
    SimulationSocketEventHandler,
)

from genworlds.events.base_event import BaseEvent
from genworlds.worlds.base_world.events import (
    EntityRequestWorldStateUpdateEvent,
    AgentSpeaksWithUserEvent,
    WorldSendsSchemasEvent,
    EntityWorldStateUpdateEvent,
    WorldSendsAllEntitiesEvent,
)
from genworlds.utils.logging_factory import LoggingFactory


class BaseAgent(SimulationSocketEventHandler):
    """
    Base GenWorlds Agent class.
    """

    world_spawned_id: str
    personality_db = None

    def __init__(
        self,
        name: str,
        description: str,
        goals: List[str],
        state_manager: StateManager,
        action_planner: ActionPlanner,
        action_validator: ActionValidator,
        action_thought_map: dict,
        id: str = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        self.id = id if id else str(uuid4())
        super().__init__(
            id=self.id,
            websocket_url=websocket_url,
        )

        # Its own properties
        self.name = name
        self.description = description
        self.goals = goals
        self.state = state_manager
        self.state["id"] = self.id  # update id

        # Helpers
        self.state_manager = state_manager
        self.action_planner = action_planner
        self.action_validator = action_validator

        # Logger
        self.logger = LoggingFactory.get_logger(self.name)

        # Agent actions
        self.actions = []

        # Thought properties
        self.action_thought_map = action_thought_map

        self.full_message_history: List[BaseMessage] = []
        self.next_action_count = 0
        self.plan: Optional[str] = None

        self.register_event_listeners(
            [
                [WorldSendsSchemasEvent, self.state_manager.update_schemas],
                [EntityWorldStateUpdateEvent, self.state_manager.update_world_state],
                [WorldSendsAllEntitiesEvent, self.state_manager.update_all_entities],
                [BaseEvent, self.state_manager.listen_for_events],
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
        updated_state = self.state_manager.get_updated_state()

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
            self.action_planner.plan_next_action()  # estas variables
            navigation_plan_parsed = self.navigation_thought.run(
                {
                    "goals": self.goals,
                    "messages": self.full_message_history,  # esta
                    "memory": self.simulation_memory,  # esta
                    "personality_db": self.personality_db,
                    "all_entities": list(
                        filter(
                            lambda e: (e["held_by"] != self.id),
                            self.all_entities.values(),  # esta
                        )
                    ),
                    "inventory": list(
                        filter(
                            lambda e: (e["held_by"] == self.id),
                            self.all_entities.values(),  # esta
                        )
                    ),
                    "plan": self.plan,
                    "user_input": user_input,
                    "agent_world_state": agent_world_state,  # esta
                    "relevant_commands": relevant_commands,  # esta
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
                    action_brains = self.action_thought_map[selected_action][
                        "thought_chain"
                    ]
                    if len(next_actions) == 0:
                        next_actions = self.action_thought_map[selected_action][
                            "next_actions"
                        ]
                else:
                    action_brains = self.action_thought_map["default"]["thought_chain"]
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
                                "command_to_execute": selected_command,
                                "previous_brain_outputs": previous_brain_outputs,
                            }
                        )
                    )
                final_brain_output = previous_brain_outputs[-1]
                try:
                    args = final_brain_output

                    if type(args) == dict:
                        print("ep")
                        event_sent = self.execute_event_with_args(
                            selected_command["title"], args
                        )
                        if not isinstance(event_sent, dict):
                            raise ValueError(
                                f"Expected a dictionary, but got {type(event_sent)}: {event_sent}"
                            )
                        print(event_sent)
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

    def launch(self):
        self.launch_websocket_thread()
        sleep(0.1)
        threading.Thread(
            target=self.think,
            name=f"Agent {self.name} Thinking Thread",
            daemon=True,
        ).start()
        self.logger.info("Threads launched")
