import time
import os
import threading

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

from genworlds.simulation.sockets.simulation_socket_client import SimulationSocketClient
from genworlds.interfaces.cli.event_processors import process_event_router
from genworlds.interfaces.cli.initial_setup_layout_screen import (
    initial_setup_layout_screen,
)
from genworlds.interfaces.cli.render_main_screen import render_main_screen

if os.getenv("IS_REPLIT") == "True":
    GENWORLDS_CONFIG_PATH = os.path.join(os.getcwd(), ".replit_config")
else:
    GENWORLDS_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".genworlds")


class CLI:
    def __init__(self):
        self.ws_client = SimulationSocketClient(self.process_event, log_level="ERROR")
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
        process_event_router(self, ws_json_message)

    def initialize_dynamic_layout(self):
        for screen in self.configuration["screens"]:
            self.screens[screen["name"]] = {}
            self.screens[screen["name"]]["has_input"] = screen["has_input"]
            self.screens[screen["name"]]["screen_type"] = screen["screen_type"]
            self.screens[screen["name"]]["buffer"] = Buffer()
            if self.screens[screen["name"]]["screen_type"] == "event_history":
                self.screens[screen["name"]]["tracked_events"] = screen[
                    "tracked_events"
                ]
            elif (
                self.screens[screen["name"]]["screen_type"] == "entities_current_state"
            ):
                self.screens[screen["name"]]["tracked_entities"] = screen[
                    "tracked_entities"
                ]

        render_main_screen(self)

    def run(self):
        time.sleep(2)
        threading.Thread(
            target=self.ws_client.websocket.run_forever,
            name=f"CLI Socket Client Thread",
            daemon=True,
        ).start()
        self.application.run()
