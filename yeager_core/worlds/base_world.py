import json
import asyncio
from typing import List, Dict, Callable, Any

from pydantic import BaseModel

from yeager_core.agents.base_gen_agent import GenerativeAgent
from yeager_core.worlds.base_object import BaseObject
from yeager_core.worlds.websocket_manager import WebSocketManager
from yeager_core.worlds.world_updates import update_dynamic_world


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
        updates = update_dynamic_world(self)
        return updates

    async def launch(self, callbacks: List[Callable] = [], time_step: float = 1.0):
        for agent in self.agents:
            agent.autonomous_run()
        while True:
            updates = await self.update_world_state()
            update_data = {"step": self.current_step, "updates": updates}
            await self.websocket_manager.send_update(
                json.dumps(update_data)
            )  # Send the update to all connected agents
            self.current_step += 1
            await asyncio.sleep(time_step)
