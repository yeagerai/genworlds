from typing import List

from yeager_core.sockets.world_socket_client import WorldSocketClient


class ListeningAntena:
    def __init__(
        self,
        world_socket_client: WorldSocketClient,
        important_event_types: List[str],
        agent_name,
        agent_id,
    ):
        self.world_socket_client = world_socket_client
        self.important_event_types = important_event_types
        self.all_events: List = []
        self.last_events: List = []
        self.agent_name = agent_name
        self.agent_id = agent_id

    async def process_event(self, event):
        if event["event_type"] in self.important_event_types:
            self.last_events.append(event)
            self.all_events.append(event)

    async def listen(self):
        print(f"The agent {self.agent_name} is listening...")
        try:
            await self.world_socket_client.message_handler(self.process_event)
        except Exception as e:
            print(f"Exception: {type(e).__name__}, {e}")
            import traceback

            traceback.print_exc()

    def get_last_events(self):
        events_to_return = self.last_events
        self.last_events = []
        return events_to_return

    def get_all_events(self):
        return self.all_events
