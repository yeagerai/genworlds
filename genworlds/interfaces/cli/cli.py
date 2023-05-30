import time
import os
import threading

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.layout import Layout

from genworlds.sockets.world_socket_client import WorldSocketClient
from genworlds.sockets.world_socket_server import (
    start_thread as start_world_socket_server_thread,
)

from genworlds.interfaces.cli.styles import init_style
from genworlds.interfaces.cli.keybindings import init_keybindings
from genworlds.interfaces.cli.event_processors import process_event_router

class CLI:
    def __init__(self):
        self.ws_client = WorldSocketClient(self.process_event)
        self.layout_initialized = False
        self.terminal_size = os.get_terminal_size()
        self.header_buffer = Buffer()
        self.menu_buffer = Buffer()
        self.menu_items = {}
        self.menu_highlighted_index = 0
        self.root_container = self.loading_layout_screen()

        self.kb = init_keybindings()
        self.style = init_style()
        self.layout = Layout(self.root_container)
        self.application = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            mouse_support=True,
            full_screen=True,
        )

    def process_event(self, ws_json_message):
        process_event_router(
            self.terminal_size, self.layout_initialized, ws_json_message
        )

    def run(self):
        start_world_socket_server_thread(silent=True)
        time.sleep(2)
        threading.Thread(
            target=self.ws_client.websocket.run_forever,
            name=f"CLI Chat Room Thread",
            daemon=True,
        ).start()
        time.sleep(2)
        self.application.run()
