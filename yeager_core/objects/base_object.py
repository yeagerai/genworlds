from uuid import uuid4
from yeager_core.events.websocket_event_handler import WebsocketEventHandler
from yeager_core.events.basic_events import (
    AgentGetsObjectInfoEvent,
    ObjectSendsInfoToAgentEvent,
)


class BaseObject(WebsocketEventHandler):
    def __init__(
        self,
        name: str,
        description: str,
        id: str = None,
    ):
        self.id = id if id else str(uuid4())
        self.name = name
        self.description = description

        super().__init__(self.id)
        self.register_event_listeners([
            # (AgentGetsObjectInfoEvent, self.agent_gets_object_info_listener)
        ])

    def agent_gets_object_info_listener(self, event: AgentGetsObjectInfoEvent):
        
        self.send_event(ObjectSendsInfoToAgentEvent,
            target_id=event.agent_id,
            object_name=self.name,
            object_description=self.description,
            possible_events=self.event_classes.keys(),
        )
