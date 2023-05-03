from time import sleep
import json
import websockets


class WorldSocketClient:
    def __init__(self) -> None:
        self.uri = "ws://0.0.0.0:7456/ws"
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        print(f"Connected to world socket server {self.uri}")

    async def send_message(self, message: str) -> None:
        await self.websocket.send(message)
        print(f"Message sent {message}")

    async def handler(self, process_event):
        while True:
            print("Waiting for messages...")
            # sleep(10)
            message = await self.websocket.recv()
            print(f"Message received {message}")
            await process_event(json.loads(message))

    async def message_handler(self, process_event) -> None:
        await self.handler(process_event)
