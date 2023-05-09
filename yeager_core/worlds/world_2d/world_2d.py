from typing import List, Type

from pydantic import BaseModel
from yeager_core.events.base_event import EventDict, EventHandler
from yeager_core.properties.basic_properties import Coordinates, Size
from yeager_core.worlds.base_world import BaseWorld
from yeager_core.worlds.world_entity import WorldEntity

class WorldEntity2D(WorldEntity):
    position: Coordinates
    size: Size

class World2D(BaseWorld[WorldEntity2D]):
    

    def __init__(
        self,
        name: str,
        description: str,
        event_dict: EventDict,
        event_handler: EventHandler,
        important_event_types: List[str],  
        vision_radius: float = 1000.0,
    ):
        super().__init__(
            world_entity_constructor=WorldEntity2D,
            name=name,
            description=description,
            event_dict=event_dict,
            event_handler=event_handler,
            important_event_types=important_event_types,
        );
    
        self.vision_radius = vision_radius


    def get_nearby_entities(self, entity_id: str) -> WorldEntity2D:
        reference_entity = self.entities.get(entity_id)
        
        nearby_entities = []
        for entity in self.entities.values():
            if entity != reference_entity:
                if reference_entity.position.distance_to(entity.position) <= self.vision_radius:
                    nearby_entities.append(entity)

        # All entities
        return nearby_entities
    

    def get_agent_world_state_prompt(self, agent_id: str) -> str:
        agent_entity = self.get_agent_by_id(agent_id)

        world_state_prompt = (
            f"You are an agent in a 2D world.\n"
            f"Your coordinates are (x={agent_entity.position.x}, y={agent_entity.position.y}).\n"
            f"Your width is {agent_entity.size.width} and your height is {agent_entity.size.height}.\n"
        )

        return world_state_prompt
