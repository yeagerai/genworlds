from __future__ import annotations
import threading
from typing import List
from genworlds.events.abstracts.action import AbstractAction
from genworlds.simulation.sockets.client import SimulationSocketClient
from genworlds.events.abstracts.event import AbstractEvent

class SimulationSocketEventHandler:
    event_actions_dict: dict[str, AbstractAction] = {}
    
    def __init__(
        self,
        id,
        actions: List[AbstractAction] = [],
        external_event_classes: dict[str, AbstractEvent] = {},
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):

        self._id = id
        self._actions = actions
        for action in self._actions:
            self.register_action(action)

        self.simulation_socket_client = SimulationSocketClient(
            process_event=self.process_event, url=websocket_url
        )

    @property
    def id(self) -> str:
        return self._id  
    
    @property
    def actions(self) -> str:
        return self._actions

    def register_action(
        self, action: AbstractAction
    ):
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
            parsed_event = self.event_actions_dict[event["event_type"]].trigger_event_class.parse_obj(event)

            for listener in self.event_actions_dict[event["event_type"]]:
                listener(parsed_event)

        if "*" in self.event_actions_dict:
            parsed_event = self.event_actions_dict[event["event_type"]].trigger_event_class.parse_obj(event)
            for listener in self.event_actions_dict["*"]:
                listener(parsed_event)

    def send_event(self, event_class: type[AbstractEvent], **kwargs):
        event = event_class(sender_id=self.id, **kwargs)

        self.simulation_socket_client.send_message(event.json())

    def launch_websocket_thread(self):
        threading.Thread(
            target=self.simulation_socket_client.websocket.run_forever,
            name=f"{self.id} Thread",
            daemon=True,
        ).start()
