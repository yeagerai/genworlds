from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension as D


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
        content=BufferControl(buffer=self.menu_items["User Interactions"]["buffer"]),
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
