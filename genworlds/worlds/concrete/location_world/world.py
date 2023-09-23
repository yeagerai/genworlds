from genworlds.worlds.base_world.base_world import BaseWorld
from genworlds.worlds.base_world_entity import BaseWorldEntity
from genworlds.worlds.location_world.events import AgentMovesToNewLocation


class WorldLocationEntity(BaseWorldEntity):
    location: str = None


class LocationWorld(BaseWorld[WorldLocationEntity]):
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
            world_entity_constructor=WorldLocationEntity,
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

    def get_same_location_entities(self, entity_id: str) -> WorldLocationEntity:
        reference_entity = self.entities.get(entity_id)

        same_location_entities = []
        # Same location or in my inventory
        for entity in self.entities.values():
            if entity != reference_entity:
                if (
                    entity.location == reference_entity.location
                    or entity.held_by == reference_entity.id
                ):
                    same_location_entities.append(entity)

        # Add objects in inventory of same_location entities
        for entity in self.entities.values():
            if entity.held_by in [e.id for e in same_location_entities]:
                same_location_entities.append(entity)

        # All entities
        return same_location_entities

    def get_agent_world_state_prompt(self, agent_id: str) -> str:
        agent_entity = self.get_agent_by_id(agent_id)

        world_state_prompt = (
            f"You are an agent in a Location world.\n"
            f'The id of the world is "{self.id}".\n'
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
