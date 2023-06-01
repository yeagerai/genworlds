from __future__ import annotations

from prompt_toolkit import Application
from prompt_toolkit.layout import HSplit, VSplit, Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.widgets import RadioList
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.widgets import Button
from prompt_toolkit.layout import WindowAlign
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.keys import Keys

import genworlds.interfaces as interfaces


def loading_socket_servers():
    ## gather all the ws running locally if is empty display the empty message
    socket_servers_menu = RadioList(
        values=[
            ("ws://0.0.0.0:7456/", "All-in Pod - ws://0.0.0.0:7456/"),
            ("ws://0.0.0.0:7457/", "Longevity Research Tank - ws://0.0.0.0:7457/"),
            ("ws://0.0.0.0:7458/", "Lawyers - ws://0.0.0.0:7458/"),
        ],
    )
    return socket_servers_menu


def loading_configuration_files(config_path):
    ## gather all the config files in the config path
    screen_config_menu = RadioList(
        values=[
            ("New", "New Configuration (Empty)"),
            ("path/to/config1.json", "All-in Pod (Debug)"),
            ("path/to/config2.json", "All-in Pod (Demo)"),
        ],
    )
    return screen_config_menu


# launch CLI button init the client threaded pointing to the selected ws server and switch the CLI layout
def launch_cli_button_handler():
    pass


def initial_setup_layout_screen(cli: interfaces.CLI, config_path: str):
    title = Window(
        height=D.exact(3),
        content=FormattedTextControl(
            text=HTML('<style fg="orange">\n🧬🌍 GenWorlds CLI Setup Screen\n</style>')
        ),
        align=WindowAlign.CENTER,
    )
    socket_servers_menu = loading_socket_servers()
    screen_config_menu = loading_configuration_files(config_path)

    socket_server_layout = HSplit(
        [
            Window(
                content=FormattedTextControl(
                    text="Select the URL of the World WS Server to connect to:",
                    focusable=True,
                ),
                height=1,
                style="reverse",
            ),
            socket_servers_menu,
        ]
    )

    screen_config_layout = HSplit(
        [
            Window(
                content=FormattedTextControl(
                    text="Select CLI Config File or start a new one:", focusable=True
                ),
                height=1,
                style="reverse",
            ),
            screen_config_menu,
        ]
    )

    main_container = VSplit([socket_server_layout, screen_config_layout])

    launch_cli_button = Button("Launch CLI", handler=launch_cli_button_handler)

    # Update the CLI layout
    cli.application.layout.container = HSplit(
        [
            title,
            main_container,
            Window(height=5),
            launch_cli_button,
            Window(height=1),
        ]
    )

    # Update initial focus
    cli.application.layout.focus(socket_servers_menu)

    # Update the CLI keybindings
    @cli.kb.add("right")
    def _(event):
        if cli.application.layout.has_focus(screen_config_menu):
            cli.application.layout.focus(launch_cli_button)
        else:
            cli.application.layout.focus(screen_config_menu)

    @cli.kb.add("left")
    def _(event):
        # focus the left RadioList
        if cli.application.layout.has_focus(launch_cli_button):
            cli.application.layout.focus(screen_config_menu)
        else:
            cli.application.layout.focus(socket_servers_menu)
