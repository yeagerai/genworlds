from time import sleep
import threading
import websocket

from colorama import Fore


class SimulationSocketClient:
    def __init__(self) -> None:
        self.uri = "ws://127.0.0.1:7456/ws"
        self.websocket = websocket.WebSocketApp(
            self.uri,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        print(f"Connected to world socket server {self.uri}")

    def on_open(self, ws):
        print(f"World socket client opened connection to {self.uri}")

    def on_message(self, ws, message):
        thread_name = threading.current_thread().name
        print(f"{Fore.GREEN}[{thread_name}] World socket client received: {message}")

    def on_error(self, ws, error):
        print(f"World socket client error: {error}")

    def on_close(self, ws):
        print("World socket client closed connection")

    def send_messages_every_10secs(self):
        thread_name = threading.current_thread().name
        while True:
            sleep(10)
            message = "Hello World!"
            self.websocket.send(message)
            print(f"{Fore.CYAN}[{thread_name}] World socket client sent: {message}")


def main():
    world_socket_client = SimulationSocketClient()
    world_socket_client_2 = SimulationSocketClient()
    world_socket_client_3 = SimulationSocketClient()

    threading.Thread(
        target=world_socket_client.websocket.run_forever, name="Listener Test Thread"
    ).start()
    threading.Thread(
        target=world_socket_client_2.websocket.run_forever,
        name="Listener Test Thread 2",
    ).start()
    threading.Thread(
        target=world_socket_client_3.websocket.run_forever,
        name="Listener Test Thread 3",
    ).start()
    threading.Thread(
        target=world_socket_client.send_messages_every_10secs, name="Sender Test Thread"
    ).start()


main()
