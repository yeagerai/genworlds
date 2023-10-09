from __future__ import annotations
from abc import ABC, abstractmethod
import json
from typing import Any, Type, TypeVar, Generic, Tuple

from genworlds.events.abstracts.event import AbstractEvent

T = TypeVar("T", bound=AbstractEvent)


class AbstractAction(ABC, Generic[T]):
    trigger_event_class: Type[T]
    description: str

    def __init__(self, host_object: "AbstractObject"):
        self.host_object = host_object

    @property
    def action_schema(self) -> Tuple(str):
        """Returns the action schema as a string"""
        return (
            f"{self.host_object.id}:{self.__class__.__name__}",
            f"{self.description}|{self.trigger_event_class.__fields__['event_type'].default}|"
            + json.dumps(self.trigger_event_class.schema()),
        )
        # f"{type(self.host_object).__name__}|\n{self.host_object.description}|\n"

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
