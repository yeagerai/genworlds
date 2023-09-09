from typing import List
from genworlds.events import BaseEvent

from genworlds.worlds.base_world import BaseObject
from genworlds.objects.base_object import BaseObject


class AgentSpeaksIntoMicrophone(BaseEvent):
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
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        super().__init__(
            name,
            description,
            id=id,
            websocket_url=websocket_url,
        )

        self.host = host

        self.register_event_listeners(
            [
                (AgentSpeaksIntoMicrophone, self.agent_speaks_into_microphone_listener),
            ]
        )

    def agent_speaks_into_microphone_listener(self, event: AgentSpeaksIntoMicrophone):
        print(f"Agent {event.sender_id} says: {event.message}.")
