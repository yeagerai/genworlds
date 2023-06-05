import argparse
import time
import os
from datetime import datetime
import threading

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
import textwrap

from genworlds.sockets.world_socket_client import WorldSocketClient
from genworlds.sockets.world_socket_server import (
    start_thread as start_world_socket_server_thread,
)


class ChatRoom:
    def __init__(self):
        self.ws_client = WorldSocketClient(self.process_event)

        self.header_buffer = Buffer()
        self.menu_buffer = Buffer()
        self.chat_buffer = Buffer()
        self.prompt_buffer = Buffer()

        self.menu_items = []
        self.menu_highlighted_index = 0

        self.init_layout()
        self.init_keybindings()
        self.init_style()
        self.init_app()

    def init_layout(self):
        header = Window(
            height=3,
            content=BufferControl(buffer=self.header_buffer),
            align=WindowAlign.LEFT,
        )
        menu_content = BufferControl(buffer=self.menu_buffer)
        switch_chat_menu = Window(
            content=menu_content,
            width=D.exact(15),
            style="class:menu",
            wrap_lines=False,
        )
        chat = Window(BufferControl(buffer=self.chat_buffer))
        chat_user_input = Window(
            height=3,
            content=BufferControl(buffer=self.prompt_buffer),
            style="class:prompt",
        )
        footer = Window(
            height=2,
            content=FormattedTextControl(
                [
                    ("class:title", "The default 🧬🌍 GenWorlds interface\n"),
                    (
                        "class:title",
                        "Press [Ctrl-S] to select chat. | Press [Ctrl-C] to quit.",
                    ),
                ]
            ),
            align=WindowAlign.CENTER,
        )

        self.root_container = HSplit(
            [
                header,
                Window(height=1, char="-", style="class:line"),
                VSplit(
                    [
                        switch_chat_menu,
                        Window(width=1, char="|", style="class:line"),
                        chat,
                    ]
                ),
                Window(height=1, char="-", style="class:line"),
                chat_user_input,
                Window(height=1, char="-", style="class:line"),
                footer,
            ]
        )

    def init_keybindings(self):
        self.kb = KeyBindings()

        @self.kb.add("c-c", eager=True)
        def exit_app(event):
            event.app.exit()

        @self.kb.add("up")
        def navigate_up(event):
            if self.menu_highlighted_index > 0:
                self.menu_highlighted_index -= 1
            self.menu_buffer.text = self._create_menu_text()

        @self.kb.add("down")
        def navigate_down(event):
            if self.menu_highlighted_index < len(self.menu_items) - 1:
                self.menu_highlighted_index += 1
            self.menu_buffer.text = self._create_menu_text()

        @self.kb.add("c-s")
        def select_item(event):
            self._handle_menu_selection()

        # Handle text changes in prompt
        self.prompt_buffer.on_text_changed += self._handle_prompt_text_changed

    def init_style(self):
        self.style = Style(
            [
                ("menu.highlighted", "fg:white bg:grey"),
                ("menu.normal", "fg:black"),
            ]
        )

    def init_app(self):
        self.application = Application(
            layout=Layout(self.root_container, focused_element=self.prompt_buffer),
            key_bindings=self.kb,
            mouse_support=True,
            full_screen=True,
            style=self.style,
        )

    def process_event(self, ws_json_message):
        # router for event types
        if ws_json_message["event_type"] == "agent_speaks_into_microphone":
            self.chat_buffer.text += self._process_agent_message(ws_json_message)
        if ws_json_message["event_type"] == "world_sends_schemas_event":
            self._process_world_state(ws_json_message)

    def run(self):
        start_world_socket_server_thread(silent=True)
        time.sleep(2)
        threading.Thread(
            target=self.ws_client.websocket.run_forever,
            name=f"CLI Chat Room Thread",
            daemon=True,
        ).start()
        self.application.run(),

    def _handle_prompt_text_changed(self, _):
        # TODO: enable chat input and chat events to chat with the agents
        pass

    def _handle_menu_selection(self):
        # TODO: switch chat window based on menu selection
        pass

    def _create_menu_text(self):
        menu_text = []
        for i, (item, _) in enumerate(self.menu_items):
            if i == self.menu_highlighted_index:
                style_class = "class:menu.highlighted"
                menu_text.append((style_class, "> "))
                menu_text.append((style_class, item))
                menu_text.append((style_class, "\n"))
            else:
                style_class = "class:menu.normal"
                menu_text.append((style_class, "  "))
                menu_text.append((style_class, item))
                menu_text.append((style_class, "\n"))
        return menu_text

    def _get_terminal_size(self):
        return os.get_terminal_size()

    def _process_world_state(self, message):
        self.header_buffer.text = (
            f"{message['world_name']}\n{message['world_description']}"
        )
        # TODO: process menu items and coloring per agent

    def _process_thoughts(self, message):
        # TODO: Add thoughts to the agent window buffer
        pass

    def _process_agent_message(self, message):
        timestamp = datetime.fromisoformat(message["created_at"].replace("Z", "+00:00"))
        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        columns, _ = self._get_terminal_size()
        wrap_width = max(
            columns - len(f"{formatted_timestamp} [{message['sender_id']}]: ") - 20, 0
        )
        wrapped_message = textwrap.fill(message["message"], wrap_width)
        return f"{formatted_timestamp} [{message['sender_id']}]: {wrapped_message}\n\n"


def start(host: str = "127.0.0.1", port: int = 7456):
    chat_room = ChatRoom()
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


# And to run the application
if __name__ == "__main__":
    chat_room = ChatRoom()
    chat_room.run()
