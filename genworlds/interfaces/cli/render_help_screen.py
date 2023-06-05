from __future__ import annotations

from prompt_toolkit.layout import HSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout import WindowAlign
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.keys import Keys

import genworlds.interfaces as interfaces
import genworlds.interfaces.cli.render_main_screen as render_main_screen


def render_help_screen(cli: interfaces.CLI):
    title = Window(
        height=D.exact(3),
        content=FormattedTextControl(
            text=HTML('<style fg="orange">\n🧬🌍 GenWorlds CLI Help Screen\n</style>')
        ),
        align=WindowAlign.CENTER,
    )

    main_container = HSplit(
        [
            Window(
                height=1,
                content=FormattedTextControl(
                    text="Press ESC to return to the main screen"
                ),
                align=WindowAlign.CENTER,
            ),
            Window(
                height=1,
                content=FormattedTextControl(
                    text="Press CTRL+W to write buffers to disk"
                ),
                align=WindowAlign.CENTER,
            ),
            Window(
                height=1,
                content=FormattedTextControl(
                    text="Press CTRL+H to view this help screen"
                ),
                align=WindowAlign.CENTER,
            ),
            Window(
                height=1,
                content=FormattedTextControl(text="Press CTRL+C to exit"),
                align=WindowAlign.CENTER,
            ),
        ]
    )

    # Update the CLI layout
    cli.application.layout.container = HSplit(
        [
            title,
            main_container,
        ],
    )

    # Update the CLI keybindings
    @cli.kb.add(Keys.Escape, eager=True)
    def _(event):
        render_main_screen.render_main_screen(cli)
