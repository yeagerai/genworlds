import threading
from typing import Callable, List
from datetime import datetime

from genworlds.simulation.sockets.client import SimulationSocketClient
from genworlds.events.base_event import BaseEvent


class SimulationSocketEventHandler:
    listeners: dict[str, set]
    event_classes: dict[str, type[BaseEvent]]

    def __init__(
        self,
        id,
        event_class_listener_pairs: List[tuple[type[BaseEvent], Callable]] = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        if event_class_listener_pairs is None:
            event_class_listener_pairs = []

        self.listeners = {}
        self.event_classes = {}

        self.id = id
        self.register_event_listeners(event_class_listener_pairs)
        self.simulation_socket_client = SimulationSocketClient(
            process_event=self.process_event, url=websocket_url
        )

    def register_event_listeners(
        self, event_class_listener_pairs: List[tuple[type[BaseEvent], Callable]]
    ):
        for event_class, event_listener in event_class_listener_pairs:
            self.register_event_listener(event_class, event_listener)

    def register_event_classes(self, event_classes: List[type[BaseEvent]]):
        for event_class in event_classes:
            event_type = event_class.__fields__["event_type"].default
            self.event_classes[event_type] = event_class

    def register_event_listener(
        self, event_class: type[BaseEvent], event_listener: Callable
    ):
        if event_class == BaseEvent:
            event_type = "*"
        else:
            event_type = event_class.__fields__["event_type"].default
        self.event_classes[event_type] = event_class

        if event_type not in self.listeners:
            self.listeners[event_type] = set()

        self.listeners[event_type].add(event_listener)

    def unregister_event_listener(
        self, event_class: type[BaseEvent], event_listener: Callable
    ):
        if event_class.event_type in self.listeners:
            self.listeners[event_class.event_type].remove(event_listener)

            if len(self.listeners[event_class.event_type]) == 0:
                del self.listeners[event_class.event_type]

    def process_event(self, event):
        if event["event_type"] in self.listeners and (
            event["target_id"] == None or event["target_id"] == self.id
        ):
            parsed_event = self.event_classes[event["event_type"]].parse_obj(event)

            for listener in self.listeners[event["event_type"]]:
                listener(parsed_event)
    
        if "*" in self.listeners:
            parsed_event = self.event_classes[event["event_type"]].parse_obj(event)
            for listener in self.listeners["*"]:
                listener(parsed_event)

    def send_event(self, event_class: type[BaseEvent], **kwargs):
        event = event_class(sender_id=self.id, created_at=datetime.now(), **kwargs)

        self.simulation_socket_client.send_message(event.json())

    def launch_websocket_thread(self):
        threading.Thread(
            target=self.simulation_socket_client.websocket.run_forever,
            name=f"{self.id} Thread",
            daemon=True,
        ).start()