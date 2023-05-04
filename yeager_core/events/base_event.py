import re
from typing import Any, Callable, List
from pydantic import BaseModel
from datetime import datetime


class Event(BaseModel):
    event_type: str
    description: str
    created_at: datetime


class Listener:
    def __init__(self, name: str, description: str, function: Callable):
        self.name = name
        self.description = description
        self.function = function


class EventHandler:
    def __init__(self):
        self.listeners = {}  # register all base listeners

    def register_listener(self, event_type: str, listener: Listener):
        if event_type not in self.listeners:
            self.listeners[event_type] = {}
        self.listeners[event_type][listener.name] = listener

    def handle_event(self, event, listener_name):
        if event.event_type in self.listeners:
            if listener_name in list(self.listeners[event.event_type].keys()):
                self.listeners[event.event_type][listener_name].function(event)


def capwords_to_snake_case(s):
    words = re.findall("[A-Z][a-z0-9]*", s)
    return "_".join([word.lower() for word in words])

def snake_to_capwords(snake_str):
    words = snake_str.split('_')
    cap_words = [word.capitalize() for word in words]
    return ''.join(cap_words)

class EventDict:
    def __init__(self):
        self.event_classes = {}  # register all base events

    def register_events(self, events: List[Any]):
        for event_class in events:
            event_type = capwords_to_snake_case(event_class.__name__)
            self.event_classes[event_type] = event_class

    def get_event_class(self, event_type: str):
        if event_type in self.event_classes:
            return self.event_classes[event_type]
        else:
            return None
