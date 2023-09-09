from uuid import uuid4
from genworlds.events.simulation_socket_event_handler import SimulationSocketEventHandler
from genworlds.events.basic_events import (
    AgentGetsObjectInfoEvent,
    ObjectSendsInfoToAgentEvent,
)


class BaseObject(SimulationSocketEventHandler):
    def __init__(
        self,
        name: str,
        description: str,
        id: str = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        self.id = id if id else str(uuid4())
        self.name = name
        self.description = description

        super().__init__(
            id=self.id,
            websocket_url=websocket_url,
        )
        self.register_event_listeners(
            [
                # (AgentGetsObjectInfoEvent, self.agent_gets_object_info_listener)
            ]
        )

    def agent_gets_object_info_listener(self, event: AgentGetsObjectInfoEvent):
        self.send_event(
            ObjectSendsInfoToAgentEvent,
            target_id=event.agent_id,
            object_name=self.name,
            object_description=self.description,
            possible_events=self.event_classes.keys(),
        )
