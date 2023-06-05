from __future__ import annotations

from datetime import datetime
import textwrap
from prompt_toolkit.buffer import Buffer
import genworlds.interfaces as interfaces


def process_event_router(self: interfaces.CLI, ws_json_message):
    if len(self.screens) > 0:
        for screen_name in self.screens:
            screen = self.screens[screen_name]
            if screen["screen_type"] == "event_history":
                if ws_json_message["event_type"] in [
                    ev["event_type"] for ev in screen["tracked_events"]
                ]:  # modify buffers accordingly
                    screen["buffer"].text += event_history_formatter(
                        screen, ws_json_message
                    )
            elif screen["screen_type"] == "entities_current_state":
                screen["buffer"].text += entities_current_state_formatter(
                    screen, ws_json_message
                )


def event_history_formatter(screen, message):
    text = ""
    event_type = message["event_type"]
    for et in screen["tracked_events"]:
        if et["event_type"] == event_type:
            for field in message:
                if field in et["fields_to_display"]:
                    if field in et["filters"]:
                        if message[field] in et["filters"][field]:
                            text += f"{field}: {message[field]}\n"
                            continue
                    else:
                        text += f"{field}: {message[field]}\n"
    # add the coloring and the formatting fit to screen size
    return text + "\n"


def entities_current_state_formatter(screen, message):
    return ""
