from __future__ import annotations

from prompt_toolkit.layout import HSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.widgets import MenuContainer, MenuItem
from prompt_toolkit.layout import WindowAlign
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.keys import Keys
from prompt_toolkit.key_binding import KeyBindings

import genworlds.interfaces as interfaces
from genworlds.interfaces.cli.render_help_screen import render_help_screen


def render_main_screen(cli: interfaces.CLI):
    title = Window(
        height=D.exact(3),
        content=FormattedTextControl(
            text=HTML('<style fg="orange">\n🧬🌍 GenWorlds CLI Main Screen\n</style>')
        ),
        align=WindowAlign.CENTER,
    )

    screens_menu = MenuContainer(
        body=Window(height=0),
        menu_items=[
            MenuItem(f"{k}  ", handler=lambda k=k: switch_buffer(k))
            for k in cli.screens.keys()
        ],
    )
    screen_buffer = Window(
        BufferControl(buffer=cli.screens[list(cli.screens.keys())[0]]["buffer"])
    )
    prompt_buffer = Window(height=1)  # TODO: Create a reasonable prompt_buffer
    main_container = HSplit(
        [
            screens_menu,
            Window(height=1),
            screen_buffer,
            Window(height=1, char="-", style="class:line"),
            prompt_buffer,
        ]
    )
    # Define the commands menu
    commands_menu = MenuContainer(
        body=Window(height=0),
        menu_items=[
            MenuItem(
                "^W - Write Buffers To Disk   "
            ),  # , handler=lambda: write_buffers(), shortcut=Keys.ControlW),
            MenuItem(
                "^H - Help   "
            ),  # , handler=lambda: render_help_screen(cli), shortcut=Keys.ControlH),
            MenuItem(
                "^C - Exit   "
            ),  # , handler=lambda: cli.application.exit(), shortcut=Keys.ControlC),
        ],
    )

    # Update the CLI layout
    cli.application.layout.container = HSplit(
        [
            title,
            main_container,
            Window(height=1, char="-", style="class:line"),
            commands_menu,
            Window(height=1),
        ],
    )

    # Update initial focus
    cli.application.layout.focus(screens_menu)

    # Update the CLI keybindings
    @cli.kb.add(Keys.ControlW, eager=True)
    def _(event):
        write_buffers()

    @cli.kb.add(Keys.ControlH, eager=True)
    def _(event):
        render_help_screen(cli)

    def switch_buffer(screen_name):
        screen_buffer.content = BufferControl(buffer=cli.screens[screen_name]["buffer"])
        if cli.screens[screen_name]["has_input"]:
            """TODO: If the screen has input, focus the prompt buffer and create a reasonable prompt_buffer"""
        cli.application.layout.focus(screens_menu)

    def write_buffers():
        # for screen_name in cli.screens.keys():
        #     with open(screen_name, "w") as f:
        #         f.write(cli.screens[screen_name]["buffer"].text)
        cli.application.layout.focus(screens_menu)
