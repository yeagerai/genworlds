from typing import Dict, Callable, List
from pydantic import BaseModel


class BaseObject(BaseModel):
    name: str
    description: str
    interactions: Dict[str, Callable]
    data: Dict
    position: List[float] = [0, 0, 0]
    size: List[float] = [1, 1, 1]
