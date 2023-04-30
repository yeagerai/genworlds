from typing import List

from yeager_core.sockets.world_socket_client import WorldSocketClient


class ListeningAntena:
    def __init__(
        self, world_socket_client: WorldSocketClient, important_event_types: List[str]
    ):
        self.world_socket_client = world_socket_client
        self.important_event_types = important_event_types
        self.all_events = []
        self.last_events = []

    async def listen(self):
        while True:
            with self.world_socket_client.ws_connection as websocket:
                event = await websocket.recv()
                if event["event_type"] in self.important_event_types:
                    self.last_events.append(event)
                    self.all_events.append(event)

    def get_last_events(self):
        events_to_return = self.last_events
        self.last_events = []
        return events_to_return

    def get_all_events(self):
        return self.all_events
