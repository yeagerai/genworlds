import os
import sys
import argparse
import threading
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn


GENWORLDS_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".genworlds")
if not os.path.exists(GENWORLDS_CONFIG_PATH):
    os.mkdir(GENWORLDS_CONFIG_PATH)


def write_socket_server_to_file(url: str):
    with open(
        os.path.join(GENWORLDS_CONFIG_PATH, "active_socket_servers_list.txt"), "a"
    ) as f:
        f.write(f"{url}\n")


def remove_socket_server_from_file(url: str):
    with open(
        os.path.join(GENWORLDS_CONFIG_PATH, "active_socket_servers_list.txt"), "r"
    ) as f:
        lines = f.readlines()
    with open(
        os.path.join(GENWORLDS_CONFIG_PATH, "active_socket_servers_list.txt"), "w"
    ) as f:
        for line in lines:
            if f"{url}" not in line:
                f.write(line)


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
    print("SIGTERM received, stopping server...")
    remove_socket_server_from_file(socket_server_url)
    sys.exit(0)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await websocket_manager.send_update(data)
    except WebSocketDisconnect as e:
        print(f"WebSocketDisconnect: {e.code}")
    except Exception as e:
        print(f"Exception: {type(e).__name__}, {e}")
        import traceback

        traceback.print_exc()
    finally:
        await websocket_manager.disconnect(websocket)


def start(host: str = "127.0.0.1", port: int = 7456, silent: bool = False):
    if silent:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

    uvicorn.run(app, host=host, port=port, log_level="info")

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


def start_from_command_line():
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

    args = parser.parse_args()

    port = args.port
    host = args.host
    global socket_server_url
    socket_server_url = f"http://{host}:{port}"

    write_socket_server_to_file(socket_server_url)
    try:
        start(host=host, port=port)
    except BaseException as e:
        print(f"{e}")
        remove_socket_server_from_file(socket_server_url)
        sys.exit(0)


if __name__ == "__main__":
    start_from_command_line()
