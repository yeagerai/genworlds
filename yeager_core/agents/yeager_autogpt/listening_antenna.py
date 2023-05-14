from yeager_core.sockets.world_socket_client import WorldSocketClient
from langchain.schema import Document

class ListeningAntenna:
    agent_world_state = "You have not yet learned about the world state."
    schemas : dict = {}
    nearby_entities: list = []

    important_event_types: set[str]

    all_events: list = []
    last_events: list = []
    agent_name: str
    agent_id: str

    def __init__(
        self,
        important_event_types: set[str],
        agent_name,
        agent_id,
    ):
        self.world_socket_client = WorldSocketClient(process_event=self.process_event)
        self.important_event_types = {"world_sends_schemas_event", "entity_world_state_update_event", "world_sends_nearby_entities_event"}.update(important_event_types)
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
        elif event["target_id"] == self.agent_id or event["event_type"] in self.important_event_types:
            self.last_events.append(event)
            self.all_events.append(event)

    def get_last_events(self):
        events_to_return = self.last_events
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
