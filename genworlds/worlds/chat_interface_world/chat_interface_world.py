import json

from genworlds.worlds.base_world.base_world import BaseWorld
from genworlds.worlds.base_world.base_world_entity import BaseWorldEntity
from genworlds.worlds.chat_interface_world.events import (
    UserRequestsScreensToWorld,
    WorldSendsScreensToUser,
)


class ChatInterfaceWorld(BaseWorld[BaseWorldEntity]):
    def __init__(
        self,
        name: str,
        description: str,
        id: str = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
        screens_config_path: str = "./screens_config.json",
    ):
        super().__init__(
            world_entity_constructor=BaseWorldEntity,
            name=name,
            description=description,
            id=id,
            websocket_url=websocket_url,
        )

        self.screens_config_path = screens_config_path
        self.screens_config = json.load(open(self.screens_config_path))

        self.register_event_listeners(
            [
                (UserRequestsScreensToWorld, self.send_screens_to_user_listener),
            ]
        )

    def send_screens_to_user_listener(self, event: UserRequestsScreensToWorld):
        self.send_event(
            WorldSendsScreensToUser(
                sender_id=self.id,
                target_id=event.sender_id,
                screens_config=self.screens_config,
            )
        )

    def get_agent_world_state_prompt(self, agent_id: str) -> str:
        agent_entity = self.get_agent_by_id(agent_id)

        world_state_prompt = (
            f"You are an agent in a Chat based World.\n"
            f'The id of the world is "{self.id}".\n'
            f'Your id is "{agent_entity.id}".\n'
            f"Expect to send and receive messages to other users and agents.\n"
        )

        return world_state_prompt
