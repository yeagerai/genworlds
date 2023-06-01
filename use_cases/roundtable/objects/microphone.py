from typing import List
from genworlds.events.websocket_event_handler import Event

from genworlds.worlds.base_world import BaseObject
from genworlds.objects.base_object import BaseObject


class AgentSpeaksIntoMicrophone(Event):
    event_type = "agent_speaks_into_microphone"
    description = "The holder of the microphone speaks into the microphone"
    message: str


class Microphone(BaseObject):
    host: str

    def __init__(
        self,
        name: str,
        description: str,
        host: str,
        id: str = None,
    ):
        super().__init__(
            name,
            description,
            id=id,
        )

        self.host = host
        self.holder = host

        self.register_event_listeners(
            [
                (AgentSpeaksIntoMicrophone, self.agent_speaks_into_microphone_listener),
            ]
        )

    def agent_speaks_into_microphone_listener(self, event: AgentSpeaksIntoMicrophone):
        if event.sender_id != self.holder:
            print(f"Agent {event.sender_id} is not the holder of the microphone.")
            return
        print(f"Agent {event.sender_id} says: {event.message}.")
