from prompt_toolkit.styles import Style

def init_style():
    return Style(
        [
            ("menu.highlighted", "fg:white bg:grey"),
            ("menu.normal", "fg:black"),
        ]
    )
