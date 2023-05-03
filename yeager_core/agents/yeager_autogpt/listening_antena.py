from typing import List

from yeager_core.sockets.world_socket_client import WorldSocketClient


class ListeningAntena:
    def __init__(
        self,
        important_event_types: List[str],
        agent_name,
        agent_id,
    ):
        self.world_socket_client = WorldSocketClient(process_event=self.process_event)
        self.important_event_types = important_event_types
        self.all_events: List = []
        self.last_events: List = []
        self.agent_name = agent_name
        self.agent_id = agent_id

    def process_event(self, event):
        if event["event_type"] in self.important_event_types:
            self.last_events.append(event)
            self.all_events.append(event)

    def get_last_events(self):
        events_to_return = self.last_events
        self.last_events = []
        return events_to_return

    def get_all_events(self):
        return self.all_events
