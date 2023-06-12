from genworlds.sockets.world_socket_client import WorldSocketClient
from langchain.schema import Document


class ListeningAntenna:
    special_events: set[str]
    agent_world_state = "You have not yet learned about the world state."
    schemas: dict
    nearby_entities: list

    important_event_types: set[str]

    all_events: list
    last_events: list
    agent_name: str
    agent_id: str

    def __init__(
        self,
        important_event_types: set[str],
        agent_name,
        agent_id,
        wakeup_events: dict = {},
        wakeup_callback: callable = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        self.world_socket_client = WorldSocketClient(
            process_event=self.process_event, url=websocket_url
        )

        self.websocket_url = websocket_url

        self.special_events = {
            "world_sends_schemas_event",
            "entity_world_state_update_event",
            "world_sends_nearby_entities_event",
            "world_sends_all_entities_event",
        }
        self.schemas = {}
        self.nearby_entities = []
        self.all_events = []
        self.last_events = []

        self.important_event_types = self.special_events.copy()
        self.important_event_types.update(important_event_types)

        self.wakeup_events = wakeup_events
        self.wakeup_callback = wakeup_callback

        self.agent_name = agent_name
        self.agent_id = agent_id

    def process_event(self, event):
        if event["event_type"] == "world_sends_schemas_event":
            self.schemas = event["schemas"]
        elif event["event_type"] == "entity_world_state_update_event":
            if event["target_id"] == self.agent_id:
                self.agent_world_state = event["entity_world_state"]
        elif event["event_type"] == "world_sends_nearby_entities_event":
            if event["target_id"] == self.agent_id:
                self.nearby_entities = event["nearby_entities"]
        elif event["event_type"] in self.special_events:
            # Ignore other "subconscious" events
            return
        elif (
            event["sender_id"] != self.agent_id 
            and
            (event["target_id"] == self.agent_id or 
            event["target_id"] == None or
            event["event_type"] in self.important_event_types)
        ):
            self.last_events.append(event)
            self.all_events.append(event)

        # Check if the agent needs to be woke
        self.handle_wakeup(event)

    def get_last_events(self):
        events_to_return = self.last_events.copy()
        self.last_events = []
        return events_to_return

    def get_all_events(self):
        return self.all_events

    def get_agent_world_state(self):
        return self.agent_world_state

    def get_nearby_entities(self):
        return self.nearby_entities

    def get_schemas(self):
        return self.schemas

    def handle_wakeup(self, event):
        if self.wakeup_callback == None:
            return

        event_type = event["event_type"]
        if event_type not in self.wakeup_events:
            return

        wakeup_event_property_filters = self.wakeup_events[event_type]

        # Check if the event matches the filters
        is_match = True
        for wakeup_event_property in wakeup_event_property_filters.keys():
            expected_value = wakeup_event_property_filters[wakeup_event_property]
            if event[wakeup_event_property] != expected_value:
                is_match = False
                break

        if is_match:
            self.wakeup_callback(event)
