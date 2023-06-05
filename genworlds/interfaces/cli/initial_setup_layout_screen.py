from __future__ import annotations

import os
import json
from functools import partial

from prompt_toolkit.layout import HSplit, VSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import RadioList
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.widgets import Button
from prompt_toolkit.layout import WindowAlign
from prompt_toolkit.layout.dimension import D

import genworlds.interfaces as interfaces


def loading_socket_servers(genworlds_path: str):
    ## gather all the ws running locally if is empty display the empty message
    file_path = os.path.join(genworlds_path, "active_socket_servers_list.txt")
    values = []

    with open(file_path, "r") as f:
        config = f.readlines()
    for line in list(set(config)):
        values.append((line, line))

    socket_servers_menu = RadioList(
        values=values,
    )
    return socket_servers_menu


def loading_configuration_files(genworlds_path: str):
    config_path = os.path.join(genworlds_path, "cli_configurations")
    values = []

    for file in os.listdir(config_path):
        file_path = os.path.join(config_path, file)
        with open(file_path, "r") as f:
            config = json.load(f)
        values.append((file_path, config["name"]))

    screen_config_menu = RadioList(
        values=values,
    )
    return screen_config_menu


# launch CLI button init the client threaded pointing to the selected ws server and switch the CLI layout
def launch_cli_button_handler(
    cli: interfaces.CLI, socket_servers_menu: RadioList, screen_config_menu: RadioList
):
    cli.server_url = socket_servers_menu.current_value
    with open(screen_config_menu.current_value, "r") as f:
        cli.configuration = json.load(f)
    cli.initialize_dynamic_layout()


def initial_setup_layout_screen(cli: interfaces.CLI, genworlds_path: str):
    title = Window(
        height=D.exact(3),
        content=FormattedTextControl(
            text=HTML(
                '<style fg="orange">\n🧬🌍 GenWorlds CLI Configuration Screen\n</style>'
            )
        ),
        align=WindowAlign.CENTER,
    )
    socket_servers_menu = loading_socket_servers(genworlds_path=genworlds_path)
    screen_config_menu = loading_configuration_files(genworlds_path=genworlds_path)

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

    launch_cli_button = Button(
        "Launch CLI",
        handler=partial(
            launch_cli_button_handler, cli, socket_servers_menu, screen_config_menu
        ),
    )

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
