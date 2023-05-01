from websockets.client import connect

class WorldSocketClient:
    def __init__(self) -> None:
        self.uri = "ws://localhost:7456/ws"

    async def send_message(self, message: str) -> None:
        async with connect(self.uri) as websocket:
            await websocket.send(message)

    async def handler(self, websocket, process_event):
        while True:
            message = await websocket.recv()
            await process_event(message)

    async def message_handler(self, process_event) -> None:
        async with connect(self.uri) as websocket:
            await self.handler(websocket, process_event)
