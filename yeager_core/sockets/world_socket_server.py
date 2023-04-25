from fastapi import FastAPI, WebSocket
from typing import List


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


app = FastAPI()
websocket_manager = WebSocketManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.send_update(data)

    except Exception as e:
        pass

    finally:
        await websocket_manager.disconnect(websocket)


# uvicorn world_socket_server:app --host 0.0.0.0 --port 7456
