from uuid import uuid4
import threading
from genworlds.simulation.sockets.simulation_socket_client import SimulationSocketClient


class TestUser:
    def __init__(
        self,
        name: str,
        description: str,
        id: str = None,
        websocket_url: str = "ws://127.0.0.1:7456/ws",
    ):
        self.id = id if id else str(uuid4())
        self.name = name
        self.description = description
        self.socket_client = SimulationSocketClient(
            process_event=lambda x: print("\n"), url=websocket_url
        )
        threading.Thread(
            target=self.socket_client.websocket.run_forever,
            name=f"{self.id} Thread",
            daemon=True,
        ).start()
