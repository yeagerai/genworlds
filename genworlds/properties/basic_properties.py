from uuid import uuid4
from pydantic import BaseModel


class Coordinates(BaseModel):
    x: float
    y: float

    def distance_to(self, other: "Coordinates") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Size(BaseModel):
    width: float
    height: float
