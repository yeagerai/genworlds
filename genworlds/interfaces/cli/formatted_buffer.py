from prompt_toolkit.layout.processors import (
    Processor,
    Transformation,
)
from prompt_toolkit.formatted_text import to_formatted_text
from prompt_toolkit.formatted_text.utils import fragment_list_to_text
from prompt_toolkit.formatted_text import HTML


class FormatText(Processor):
    def apply_transformation(self, ti):
        fragments = to_formatted_text(HTML(fragment_list_to_text(ti.fragments)))
        return Transformation(fragments)


def html_from_json_format(format, content):
    for el in format.split(" "):
        if el.startswith("fg:"):
            content = f'<style fg="{el[3:]}">{content}</style>'
        elif el.startswith("bg:"):
            content = f'<style bg="{el[3:]}">{content}</style>'
        elif el == "bold":
            content = f"<b>{content}</b>"
        elif el == "italic":
            content = f"<i>{content}</i>"
        elif el == "underline":
            content = f"<u>{content}</u>"
        elif el == "blink":
            content = f"<blink>{content}</blink>"
        elif el == "reverse":
            content = f"<reverse>{content}</reverse>"
        elif el == "strike":
            content = f"<strike>{content}</strike>"
    return content
