from websockets.sync.client import connect


async def handler(websocket):
    while True:
        message = await websocket.recv()
        print(message)


class WorldSocketClient:
    def __init__(self) -> None:
        self.uri = "ws://localhost:7456/ws"
        self.ws_connection = connect(self.uri)

    async def send_message(self, message: str) -> None:
        with self.ws_connection as websocket:
            websocket.send(message)

    async def message_handler(self) -> None:
        with self.ws_connection as websocket:
            await handler(websocket)
