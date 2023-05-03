import threading
import json

import websocket
from colorama import Fore


class WorldSocketClient:
    def __init__(self, process_event) -> None:
        self.uri = "ws://0.0.0.0:7456/ws"
        self.websocket = websocket.WebSocketApp(
            self.uri,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.process_event = process_event
        print(f"Connected to world socket server {self.uri}")

    def on_open(self, ws):
        print(f"World socket client opened connection to {self.uri}\n")

    def on_error(self, ws, error):
        print(f"World socket client error: {error}")

    def on_close(self, ws):
        print("World socket client closed connection")

    def on_message(self, ws, message):
        thread_name = threading.current_thread().name
        print(f"{Fore.GREEN}[{thread_name}] received: {message}")
        self.process_event(json.loads(message))

    def send_message(self, message):
        thread_name = threading.current_thread().name
        self.websocket.send(message)
        print(f"{Fore.CYAN}[{thread_name}] sent: {message}")
