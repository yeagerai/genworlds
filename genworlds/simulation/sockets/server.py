import os
import sys
import argparse
import threading
from typing import List
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_update(self, data: str):
        closed_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except RuntimeError as e:
                if "Unexpected ASGI message" in str(e) and "websocket.close" in str(e):
                    closed_connections.append(connection)
                else:
                    raise e
        for closed_connection in closed_connections:
            self.active_connections.remove(closed_connection)


app = FastAPI()
websocket_manager = WebSocketManager()

socket_server_url = None


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("SIGTERM received, stopping server...")
    sys.exit(0)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received data: {data}")
            print(data)
            await websocket_manager.send_update(data)
    except WebSocketDisconnect as e:
        logger.warning(f"WebSocketDisconnect: {e.code}")
    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}, {e}", exc_info=True)
    finally:
        await websocket_manager.disconnect(websocket)


def start(host: str = "127.0.0.1", port: int = 7456, silent: bool = False, ws_ping_interval: int = 600, ws_ping_timeout: int = 600, timeout_keep_alive: int = 60):
    if silent:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

    uvicorn.run(app, 
                host=host, 
                port=port, 
                log_level="info",
                ws_ping_interval=ws_ping_interval,
                ws_ping_timeout=ws_ping_timeout,
                timeout_keep_alive=timeout_keep_alive)  

    if silent:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def start_thread(host: str = "127.0.0.1", port: int = 7456, silent: bool = False):
    threading.Thread(
        target=start,
        name=f"Websocket Server Thread",
        daemon=True,
        args=(
            host,
            port,
            silent,
        ),
    ).start()


def parse_args():
    parser = argparse.ArgumentParser(description="Start the world socket server.")
    parser.add_argument(
        "--port",
        type=int,
        help="The port to start the socket on.",
        default=7456,
        nargs="?",
    )
    parser.add_argument(
        "--host",
        type=str,
        help="The hostname of the socket.",
        default="127.0.0.1",
        nargs="?",
    )

    return parser.parse_args()


def start_from_command_line():
    args = parse_args()
    try:
        start(host=args.host, port=args.port)
    except BaseException as e:
        logger.error(e)
        sys.exit(0)


if __name__ == "__main__":
    start_from_command_line()
