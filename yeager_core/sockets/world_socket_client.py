import json
from websockets.client import connect


class WorldSocketClient:
    def __init__(self) -> None:
        self.uri = "ws://localhost:7456/ws"
        self.websocket = None

    async def connect(self):
        self.websocket = await connect(self.uri)

    async def send_message(self, message: str) -> None:
        await self.websocket.send(message)

    async def handler(self, process_event):
        while True:
            message = await self.websocket.recv()
            await process_event(json.loads(message))

    async def message_handler(self, process_event) -> None:
        await self.handler(process_event)
