from typing import List, Dict, Callable, Any
from pydantic import BaseModel
from yeager_core.agents.base_gen_agent import GenerativeAgent
import asyncio
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        await websocket.close()

    async def send_update(self, data: str):
        for connection in self.active_connections:
            await connection.send_text(data)


class BaseObject(BaseModel):
    name: str
    description: str
    interactions: Dict[str, Callable]
    data: Dict
    position: List[float] = [0, 0, 0]
    size: List[float] = [1, 1, 1]


class BaseWorld(BaseModel):
    name: str
    description: str
    objects: List[BaseObject]
    agents: List[GenerativeAgent]
    current_step: int = 0
    websocket_manager: WebSocketManager = WebSocketManager()
    size: List[float] = [100, 100, 100]

    def add_object(self, obj: BaseObject):
        self.objects.append(obj)

    def remove_object(self, obj: BaseObject):
        self.objects.remove(obj)

    def add_agent(self, agent: GenerativeAgent):
        self.agents.append(agent)

    def remove_agent(self, agent: GenerativeAgent):
        self.agents.remove(agent)

    async def update_world_state(self):
        for obj in self.objects:
            # TODO: Update object positions, or other properties based on the world state
            obj.position = [coord + 1 for coord in obj.position]

    async def launch(self, callbacks: List[Callable] = [], time_step: float = 1.0):
        while True:
            await self.update_world_state()
            world_state = self.json()  # Serialize the current world state
            await self.websocket_manager.send_update(
                world_state
            )  # Send the update to all connected agents
            self.current_step += 1
            await asyncio.sleep(time_step)
