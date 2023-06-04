import time
import os
import threading

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings

from genworlds.sockets.world_socket_client import WorldSocketClient
from genworlds.interfaces.cli.event_processors import process_event_router
from genworlds.interfaces.cli.initial_setup_layout_screen import (
    initial_setup_layout_screen,
)
from genworlds.interfaces.cli.render_main_screen import render_main_screen

GENWORLDS_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".genworlds")


class CLI:
    def __init__(self):
        self.ws_client = WorldSocketClient(self.process_event)
        self.kb = KeyBindings()
        self.configuration = None
        self.server_url = None
        self.screens = {}
        self.current_screen = None
        self.selected_screen = None

        @self.kb.add("c-c", eager=True)
        def exit_app(event):
            event.app.exit()

        self.layout = Layout(Window())
        self.application = Application(
            layout=self.layout,
            key_bindings=self.kb,
            mouse_support=True,
            full_screen=True,
        )

        initial_setup_layout_screen(self, GENWORLDS_CONFIG_PATH)

    def process_event(self, ws_json_message):
        process_event_router(
            self.terminal_size, self.layout_initialized, ws_json_message
        )

    def initialize_dynamic_layout(self):
        for screen in self.configuration["screens"]:
            self.screens[screen["name"]] = {}
            self.screens[screen["name"]]["buffer"] = Buffer()
            self.screens[screen["name"]]["tracked_events"] = screen["tracked_events"]
        self.selected_screen = "All events"
        self.set_current_screen("All events")
        self.set_main_key_bindings()

    def set_current_screen(self, screen_name):
        self.current_screen = screen_name
        render_main_screen(self, screen_name)
        pass

    def set_main_key_bindings(self):
        pass

    def run(self):
        # threading.Thread(
        #     target=self.ws_client.websocket.run_forever,
        #     name=f"CLI Socket Client Thread",
        #     daemon=True,
        # ).start()
        time.sleep(2)
        self.application.run()
