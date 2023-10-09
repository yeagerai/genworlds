import threading
from genworlds.simulation.sockets.client import SimulationSocketClient


class TestUser:
    def __init__(
        self,
    ):
        self.id = "test_user"
        self.name = "Test User"
        self.description = "A test user for the simulation."
        self.socket_client = SimulationSocketClient(process_event=lambda x: "")
        threading.Thread(
            target=self.socket_client.websocket.run_forever,
            name=f"{self.id} Thread",
            daemon=True,
        ).start()
