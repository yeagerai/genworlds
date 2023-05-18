import threading
import json

import websocket
from colorama import Fore

from genworlds.utils.logging_factory import LoggingFactory


class WorldSocketClient:
    def __init__(self, process_event, send_initial_event=None) -> None:
        self.uri = "ws://127.0.0.1:7456/ws"
        self.websocket = websocket.WebSocketApp(
            self.uri,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.process_event = process_event
        self.send_initial_event = send_initial_event

    def on_open(self, ws):
        self.logger().info(f"Connected to world socket server {self.uri}")
        if self.send_initial_event:
            self.send_initial_event()
            self.logger().debug(f"Initial event sent")

    def on_error(self, ws, error):
        self.logger().error("World socket client error", exc_info=error)

    def on_close(self, *args):
        self.logger().info("World socket client closed connection", args)

    def on_message(self, ws, message):
        self.logger().debug(f"Received: {message}")
        if self.process_event:
            self.process_event(json.loads(message))

    def send_message(self, message):        
        self.websocket.send(message)
        self.logger().debug(f"Sent: {message}")

    def logger(self):
        return LoggingFactory.get_logger(threading.current_thread().name)
