
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.worlds.base_world import BaseWorld
from yeager_core.worlds.base_world_entity import BaseWorldEntity

class WorldEntity2D(BaseWorldEntity):
    location: str = None

class World2D(BaseWorld[WorldEntity2D]):

    locations: list[str] = []
    

    def __init__(
        self,
        name: str,
        description: str,
        locations: list[str],
        id: str = None,
    ):
        super().__init__(
            world_entity_constructor=WorldEntity2D,
            name=name,
            description=description,
            id=id,
        );
    
        self.locations = locations

    def get_nearby_entities(self, entity_id: str) -> WorldEntity2D:
        reference_entity = self.entities.get(entity_id)
        
        nearby_entities = []        
        # Same location or in my inventory
        for entity in self.entities.values():
            if entity != reference_entity:
                if entity.location == reference_entity.location or entity.held_by == reference_entity.id:
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
            f"Your id is \"{agent_entity.id}\".\n"
            f"Your location is \"{agent_entity.location}\".\n"
            f"Available locations are \"{self.locations}\".\n"
        )

        return world_state_prompt
