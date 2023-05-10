
from enum import Enum
from typing import Any, TypeVar

from pydantic import BaseModel

class EntityTypeEnum(str, Enum):
    AGENT = 'AGENT'
    OBJECT = 'OBJECT'
    WORLD = 'WORLD'

class WorldEntity(BaseModel):
    id: str
    entity_type: EntityTypeEnum
    name: str
    description: str