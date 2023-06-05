import threading
from typing import Callable, List, Optional
from pydantic import BaseModel
from datetime import datetime

from genworlds.sockets.world_socket_client import WorldSocketClient


class Event(BaseModel):
    event_type: str
    description: str
    summary: Optional[str]
    created_at: datetime
    sender_id: str
    target_id: Optional[str]


class WebsocketEventHandler:
    listeners: dict[str, set]
    event_classes: dict[str, type[Event]]

    def __init__(
        self,
        id,
        event_class_listener_pairs: List[tuple[type[Event], Callable]] = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        if event_class_listener_pairs is None:
            event_class_listener_pairs = []

        self.listeners = {}
        self.event_classes = {}

        self.id = id
        self.register_event_listeners(event_class_listener_pairs)
        self.world_socket_client = WorldSocketClient(
            process_event=self.process_event, url=websocket_url
        )

    def register_event_listeners(
        self, event_class_listener_pairs: List[tuple[type[Event], Callable]]
    ):
        for event_class, event_listener in event_class_listener_pairs:
            self.register_event_listener(event_class, event_listener)

    def register_event_listener(
        self, event_class: type[Event], event_listener: Callable
    ):
        event_type = event_class.__fields__["event_type"].default
        self.event_classes[event_type] = event_class

        if event_type not in self.listeners:
            self.listeners[event_type] = set()

        self.listeners[event_type].add(event_listener)

    def unregister_event_listener(
        self, event_class: type[Event], event_listener: Callable
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

    def send_event(self, event_class: type[Event], **kwargs):
        event = event_class(sender_id=self.id, created_at=datetime.now(), **kwargs)

        self.world_socket_client.send_message(event.json())

    def launch_websocket_thread(self):
        threading.Thread(
            target=self.world_socket_client.websocket.run_forever,
            name=f"{self.id} Thread",
            daemon=True,
        ).start()
