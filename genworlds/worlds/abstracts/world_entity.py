from abc import ABC, abstractmethod
from typing import Type, Any, Dict
from enum import Enum
from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.objects.abstracts.object import AbstractObject
from pydantic import BaseModel


class EntityTypeEnum(str, Enum):
    AGENT = "AGENT"
    OBJECT = "OBJECT"
    WORLD = "WORLD"


def get_entity_type(cls):
    from genworlds.worlds.abstracts.world import AbstractWorld

    if issubclass(cls, AbstractAgent):
        return EntityTypeEnum.AGENT
    elif issubclass(cls, AbstractWorld):
        return EntityTypeEnum.WORLD
    elif issubclass(cls, AbstractObject):
        return EntityTypeEnum.OBJECT
    else:
        return None


class AbstractWorldEntity(BaseModel, ABC):
    id: str
    entity_type: EntityTypeEnum
    entity_class: str
    name: str
    description: str

    class Config:
        extra = "allow"

    @classmethod
    def create(
        cls: Type["AbstractWorldEntity"],
        entity: AbstractObject,
        **additional_world_properties: Dict
    ) -> "AbstractWorldEntity":
        entity_cls = type(entity)
        entity_type = get_entity_type(entity_cls)
        entity_class = entity_cls.__name__
        id = entity.id
        name = entity.name
        description = entity.description
        # Combine predefined fields with any additional fields provided
        entity_data = {
            **{
                "id": id,
                "entity_type": entity_type,
                "entity_class": entity_class,
                "name": name,
                "description": description,
            },
            **additional_world_properties,
        }
        return cls(**entity_data)
