import argparse
from genworlds.interfaces import CLI

def start(host: str = "127.0.0.1", port: int = 7456):
    chat_room = CLI()
    chat_room.run()


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

    start(host=host, port=port)

if __name__ == "__main__":
    chat_room = CLI()
    chat_room.run()
