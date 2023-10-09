import threading
import json
import time

import websocket
from colorama import Fore

from genworlds.utils.logging_factory import LoggingFactory


class SimulationSocketClient:
    """
    A client for managing connections to a simulation socket server.
    """

    def __init__(
        self,
        process_event,
        url: str = "ws://127.0.0.1:7456/ws",
        send_initial_event=None,
        reconnect_interval=5,
        log_level=None,
    ) -> None:
        self.url = url
        self.websocket = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        # Callback function to process events
        self.process_event = process_event
        self.send_initial_event = send_initial_event
        self.reconnect_interval = reconnect_interval
        self.log_level = log_level

    def on_open(self, ws):
        self.logger().info(f"Connected to world socket server {self.url}")
        if self.send_initial_event:
            self.send_initial_event()
            self.logger().debug(f"Initial event sent")

    def on_error(self, ws, error):
        self.logger().error("World socket client error", exc_info=error)

    def on_close(self, *args):
        self.logger().info("World socket client closed connection", args)
        if self.reconnect_interval:
            self.logger().info(
                f"Attempting to reconnect in {self.reconnect_interval} seconds"
            )
            time.sleep(self.reconnect_interval)
            self.logger().info("Attempting to reconnect")
            self.websocket.run_forever()

    def on_message(self, ws, message):
        self.logger().debug(f"Received: {message}")
        if self.process_event:
            self.process_event(json.loads(message))

    def send_message(self, message):
        self.websocket.send(message)
        self.logger().debug(f"Sent: {message}")

    def logger(self):
        return LoggingFactory.get_logger(
            threading.current_thread().name, level=self.log_level
        )
