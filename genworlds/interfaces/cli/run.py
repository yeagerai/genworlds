import argparse
from genworlds.interfaces import CLI


def start():
    chat_room = CLI()
    chat_room.run()


if __name__ == "__main__":
    start()
