from uuid import uuid4
from pydantic import BaseModel


class Coordinates(BaseModel):
    x: float
    y: float
    z: float


class Size(BaseModel):
    width: float
    height: float
    depth: float
