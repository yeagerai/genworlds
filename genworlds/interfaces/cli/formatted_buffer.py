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


def html_from_json_format(format, content, max_width=100):
    new_lines = []
    while len(content) > max_width:
        new_lines.append(content[0:max_width])
        content = content[max_width:]
    new_lines.append(content)    
    
    new_lines_styled = [apply_style(format, line) for line in new_lines]

    return "\n".join(new_lines_styled)

def apply_style(style, content):
    for el in style.split(" "):
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
