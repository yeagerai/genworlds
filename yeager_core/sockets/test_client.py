import asyncio
import websockets
import json


class TestClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        print(f"Test client connected to {self.uri}")

    async def listen(self):
        try:
            while True:
                message = await self.websocket.recv()
                print(f"Test client received: {message}")
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Test client disconnected: {e}")


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
            message = await self.websocket.recv()
            print(f"Message received {message}")
            await process_event(json.loads(message))

    async def message_handler(self, process_event) -> None:
        await self.handler(process_event)


async def process_event(event):
    if event["event_type"] in ["agent_gets_world_objects_in_radius"]:
        print(event)
        return 0


async def main():
    test_client = WorldSocketClient()

    # Connect to the WebSocket server
    await test_client.connect()

    # Start listening for messages
    await test_client.send_message("Hello world!")


asyncio.run(main())
