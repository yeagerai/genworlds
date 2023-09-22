from typing import Optional, List

from qdrant_client import QdrantClient
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from genworlds.agents.abstracts.state_manager import AbstractStateManager

from genworlds.agents.memories.simulation_memory import SimulationMemory
from genworlds.worlds.base_world.events import (
    WorldSendsSchemasEvent,
    WorldSendsAllEntitiesEvent
)
from genworlds.utils.schema_to_model import json_schema_to_pydantic_model
from genworlds.events.abstracts.event import AbstractEvent

class StateManager(AbstractStateManager):
    agent_world_state = "You have not yet learned about the world state."

    def __init__(
        self,
        id: str,
        openai_api_key: str,
        important_event_types: set[str],
        starts_asleep: bool = False,
        interesting_events: set = {},
        wakeup_events: dict = {},
        additional_memories: Optional[List[VectorStoreRetriever]] = None,
        personality_db_qdrant_client: QdrantClient = None,
        personality_db_collection_name: str = None,
    ):
        self.agent_state = {}
        self.agent_state["id"] = id
        self.agent_state["is_asleep"] = starts_asleep
        self.agent_state["important_event_types"] = important_event_types
        self.agent_state["interesting_events"] = interesting_events
        self.agent_state["wakeup_events"] = wakeup_events
        self.agent_state["additional_memories"] = additional_memories
        self.agent_state["personality_db_qdrant_client"] = personality_db_qdrant_client
        # Memories
        self.agent_state["simulation_memory"] = SimulationMemory(
            openai_api_key=openai_api_key,
            n_of_last_events=10,
            n_of_similar_events=0,
            n_of_paragraphs_in_summary=3,
        )

        self.embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.agent_state["personality_db_qdrant_client"] = personality_db_qdrant_client
        if self.agent_state["personality_db_qdrant_client"]:
            self.personality_db = Qdrant(
                collection_name=personality_db_collection_name,
                embeddings=self.embeddings_model,
                client=self.agent_state["personality_db_qdrant_client"],
            )

        self.agent_state["special_events"] = {
            "world_sends_schemas_event",
            "entity_world_state_update_event",
            "world_sends_all_entities_event",
        }
        self.agent_state["non_memory_important_event_types"] = {
            "world_sends_schemas_event",
            "entity_world_state_update_event",
            "world_sends_all_entities_event",
        }
        self.agent_state["schemas"] = {}
        self.agent_state["event_classes"] = {}
        self.agent_state["all_entities"] = []
        self.agent_state["all_events"] = []
        self.agent_state["last_events"] = []

        self.agent_state["important_event_types"].update(self.agent_state["special_events"])

    def get_updated_state(self):
        pass

    def update_state(self):
        pass

    def get_schemas(self):
        return self.agent_state["schemas"]

    def update_schemas(self, event: WorldSendsSchemasEvent):
        self.agent_state["schemas"] = event.schemas
        self.update_event_classes_from_new_schemas(event.schemas)

    def update_event_classes_from_new_schemas(self, schemas):
        for entity in schemas:
            for event in schemas[entity]:
                Model = json_schema_to_pydantic_model(schemas[entity][event])
                event_type = Model.__fields__["event_type"].default
                if event_type not in self.agent_state["event_classes"]:
                    self.agent_state["event_classes"][event_type] = Model

    # def update_world_state(self, event: EntityWorldStateUpdateEvent):
    #     if event.target_id == self.agent_state["id"]:
    #         self.agent_world_state = event.entity_world_state

    def update_all_entities(self, event: WorldSendsAllEntitiesEvent):
        self.agent_state["all_entities"] = event.all_entities

    def listen_for_events(self, event: AbstractEvent):
        if (
            event.sender_id != self.agent_state["id"]
            and (
                event.target_id == self.agent_state["id"]
                or event.event_type in self.agent_state["important_event_types"]
            )
            and event.event_type not in self.agent_state["non_memory_important_event_types"]
        ):
            self.agent_state["last_events"].append(event)
            self.agent_state["all_events"].append(event)

    def get_last_events(self):
        events_to_return = self.last_events.copy()
        self.last_events = []
        return events_to_return

    def get_all_events(self):
        return self.agent_state["all_events"]

    # def get_agent_world_state(self):
    #     return self.agent_world_state

    def get_all_entities(self):
        return self.agent_state["all_entities"]

    def add_wakeup_event(self, event_class: AbstractEvent, params: dict):
        self.agent_state["wakeup_events"][event_class.__fields__["event_type"].default] = params
        # self.register_event_listener(event_class, self.handle_wakeup)

    def handle_wakeup(self, event):
        event_type = event.event_type
        if event_type not in self.agent_state["wakeup_events"]:
            return

        wakeup_event_property_filters = self.agent_state["wakeup_events"][event_type]

        # Check if the event matches the filters
        is_match = True
        for (
            wakeup_event_property,
            expected_value,
        ) in wakeup_event_property_filters.items():
            # Use getattr to dynamically access event attributes using their string names
            actual_value = getattr(event, wakeup_event_property, None)
            if actual_value != expected_value:
                is_match = False
                break

        if is_match:
            print("Waking up ...")
            self.agent_state["is_asleep"] = False