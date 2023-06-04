from __future__ import annotations

from prompt_toolkit.layout import HSplit, VSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl, BufferControl
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.widgets import MenuContainer, MenuItem
from prompt_toolkit.layout import WindowAlign
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.keys import Keys
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document

import genworlds.interfaces as interfaces

def render_main_screen(cli: interfaces.CLI, screen_name: str):
    title = Window(
        height=D.exact(3),
        content=FormattedTextControl(
            text=HTML('<style fg="orange">\n🧬🌍 GenWorlds CLI Main Screen\n</style>')
        ),
        align=WindowAlign.CENTER,
    )

    menu_text = "\n".join(cli.screens.keys())
    menu_buffer = Buffer(document=Document(menu_text, cursor_position=len(menu_text)))
    
    menu_content = BufferControl(buffer=menu_buffer)
    screens_menu = Window(content=menu_content, width=D.exact(15), style="class:menu", wrap_lines=False)
    screen_buffer = Window(BufferControl(buffer=cli.screens[screen_name]["buffer"]))

    main_container = VSplit([
        screens_menu, 
        Window(width=1, char="|", style="class:line"),
        screen_buffer
    ])

    # Define the commands menu
    commands_menu = MenuContainer(
        body=Window(height=0),
        menu_items=[
            MenuItem("^N - New Screen", handler=lambda: cli.show_new_screen()),
            MenuItem("^H - Help", handler=lambda: cli.show_help_screen()),
            MenuItem("^C - Exit", handler=lambda: cli.application.exit()),
        ],
    )

    # Update the CLI layout
    cli.application.layout.container = HSplit(
        [
            title,
            Window(height=1, char="-", style="class:line"),
            main_container,
            Window(height=1, char="-", style="class:line"),
            commands_menu,
            Window(height=1),
        ]
    )
    
    # Update the CLI keybindings
    @cli.kb.add("up")
    def _(event):
        # move the selected item in the screens_menu up
        pass
    
    @cli.kb.add("down")
    def _(event):
        # move the selected item in the screens_menu down
        pass

    @cli.kb.add(Keys.Enter)
    def _(event):
        # renders the buffer selected in the screens_menu
        pass

    @cli.kb.add("c-h")
    def _(event):
        # opens the help screen
        pass

