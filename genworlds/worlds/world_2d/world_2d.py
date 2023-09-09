from genworlds.events import BaseEvent
from genworlds.worlds.base_world import BaseWorld
from genworlds.worlds.base_world_entity import BaseWorldEntity


class WorldEntity2D(BaseWorldEntity):
    location: str = None


class AgentMovesToNewLocation(BaseEvent):
    event_type = "agent_moves_to_new_location"
    description = "Agent moves to a new location in the world."
    destination_location: str


class World2D(BaseWorld[WorldEntity2D]):
    locations: list[str] = []

    def __init__(
        self,
        name: str,
        description: str,
        locations: list[str],
        id: str = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        super().__init__(
            world_entity_constructor=WorldEntity2D,
            name=name,
            description=description,
            id=id,
            websocket_url=websocket_url,
        )

        self.locations = locations

        self.register_event_listeners(
            [
                (AgentMovesToNewLocation, self.agent_moves_to_new_location_listener),
            ]
        )

    def get_nearby_entities(self, entity_id: str) -> WorldEntity2D:
        reference_entity = self.entities.get(entity_id)

        nearby_entities = []
        # Same location or in my inventory
        for entity in self.entities.values():
            if entity != reference_entity:
                if (
                    entity.location == reference_entity.location
                    or entity.held_by == reference_entity.id
                ):
                    nearby_entities.append(entity)

        # Add objects in inventory of nearby entities
        for entity in self.entities.values():
            if entity.held_by in [e.id for e in nearby_entities]:
                nearby_entities.append(entity)

        # All entities
        return nearby_entities

    def get_agent_world_state_prompt(self, agent_id: str) -> str:
        agent_entity = self.get_agent_by_id(agent_id)

        world_state_prompt = (
            f"You are an agent in a 2D world.\n"
            f'THe id of the world is "{self.id}".\n'
            f'Your id is "{agent_entity.id}".\n'
            f'Your location is "{agent_entity.location}".\n'
            f'Available locations are "{self.locations}".\n'
        )

        return world_state_prompt

    def agent_moves_to_new_location_listener(self, event: AgentMovesToNewLocation):
        agent_entity = self.get_agent_by_id(event.agent_id)

        if event.destination_location not in self.locations:
            raise Exception(f"Location {event.destination_location} does not exist.")

        agent_entity.location = event.destination_location
        self.emit_agent_world_state(agent_entity.id)

    def add_location(self, location: str):
        self.locations.append(location)

    def remove_location(self, location: str):
        self.locations.remove(location)