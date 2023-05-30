import time

from prompt_toolkit.layout.containers import Window, HSplit, VSplit, FloatContainer, Float
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout import DynamicContainer
from prompt_toolkit.widgets import Box, Frame
from prompt_toolkit.output import ThreadedGenerator

def loading_animation(self):
    for i in range(4):
        yield f"Loading the 🧬🌍 GenWorlds CLI {'.'*i}"
        time.sleep(0.5)

def loading_layout_screen(self):
    control = FormattedTextControl(
        ThreadedGenerator(self.loading_animation), focusable=False)
    return FloatContainer(
        content=HSplit(
            [
                Window(height=D.exact(1)),
                VSplit(
                    [
                        Window(width=D.exact(1)),
                        Box(Frame(body=Window(content=control))),
                        Window(width=D.exact(1)),
                    ]
                ),
                Window(height=D.exact(1)),
            ]
        ),
        floats=[
            Float(xcursor=True, ycursor=True,
                    content=Window(control, height=1, width=9))
        ],
    )