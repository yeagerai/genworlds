from __future__ import annotations
from uuid import uuid4
import threading
from typing import List
from genworlds.events.abstracts.action import AbstractAction
from genworlds.simulation.sockets.client import SimulationSocketClient
from genworlds.events.abstracts.event import AbstractEvent


class SimulationSocketEventHandler:
    def __init__(
        self,
        id: str,
        actions: List[AbstractAction] = [],
        external_event_classes: dict[str, AbstractEvent] = {},
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        self.event_actions_dict: dict[str, AbstractAction] = {}
        self.id = id if id else str(uuid4())
        self.actions = actions
        for action in self.actions:
            self.register_action(action)

        self.simulation_socket_client = SimulationSocketClient(
            process_event=self.process_event, url=websocket_url
        )

    def register_action(self, action: AbstractAction):
        event_type = action.trigger_event_class.__fields__["event_type"].default
        if event_type not in self.event_actions_dict:
            self.event_actions_dict[event_type] = []
            self.event_actions_dict[event_type].append(action)
        else:
            self.event_actions_dict[event_type].append(action)

    def process_event(self, event):
        if event["event_type"] in self.event_actions_dict and (
            event["target_id"] == None or event["target_id"] == self.id
        ):
            # 0 bc the trigger_event_class is the same for all actions with the same event_type
            parsed_event = self.event_actions_dict[event["event_type"]][
                0
            ].trigger_event_class.parse_obj(event)

            for listener in self.event_actions_dict[event["event_type"]]:
                listener(parsed_event)

        if "*" in self.event_actions_dict:
            for listener in self.event_actions_dict["*"]:
                listener(event)

    def send_event(self, event: AbstractEvent):
        self.simulation_socket_client.send_message(event.json())

    def launch_websocket_thread(self):
        threading.Thread(
            target=self.simulation_socket_client.websocket.run_forever,
            name=f"{self.id} Thread",
            daemon=True,
        ).start()
