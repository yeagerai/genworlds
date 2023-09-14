import threading
from time import sleep
from genworlds.simulation.simulation import Simulation
from genworlds.simulation.sockets.server import start


def launch_simulation(simulation: Simulation):
    # Start the simulation socket in a parallel thread
    simulation_socket = threading.Thread(target=start)
    simulation_socket.start()

    # Wait for the socket to start
    sleep(1)

    # Launch the simulation
    simulation_thread = threading.Thread(target=simulation.launch)
    simulation_thread.start()
