from __future__ import annotations
from abc import ABC, abstractmethod

from typing import Any, Type, TypeVar, Generic

from genworlds.events.abstracts.event import AbstractEvent

T = TypeVar("T", bound=AbstractEvent)
class AbstractAction(ABC, Generic[T]):
    trigger_event_class: Type[T]

    def __init__(self, host_object: "AbstractObject"):
        self.host_object = host_object
        
    @property
    @classmethod
    def action_schema(self) -> str:
        """Returns the action schema as a string"""
        return f"{self.host_object.id}:{type(self.host_object).__name__}:{self.trigger_event_class.event_type}:{self.trigger_event_class.schema()}"
    
    @abstractmethod
    def __call__(self, event: T, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the action, potentially generating one or more events.
        Send the events with self.socket_handler.send_event(event).

        :param event: The event that triggers the action.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: The result of the action execution. The type of the return value can be any type 
                 depending on the implementation.
        """
        pass