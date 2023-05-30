from datetime import datetime
import textwrap
from prompt_toolkit.buffer import Buffer

def process_event_router(terminal_size, layout_initialized, ws_json_message):
    initial_layout = {}
    if (
        ws_json_message["event_type"] == "world_sends_all_entities_event"
    ):  # create layout
        if layout_initialized == False:
            initial_layout["header_buffer"], initial_layout["menu_items"] = process_initial_world_state(ws_json_message)
            layout_initialized = True

    new_chat_message = ""
    if ws_json_message["event_type"] == "agent_speaks_into_microphone":
        new_chat_message += process_agent_message(terminal_size, ws_json_message)

    return initial_layout, new_chat_message, layout_initialized

def process_thoughts(message):
    # TODO: Add thoughts to the agent window buffer
    pass

def process_agent_message(terminal_size, message):
    timestamp = datetime.fromisoformat(message["created_at"].replace("Z", "+00:00"))
    formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    wrap_width = max(
        terminal_size - len(f"{formatted_timestamp} [{message['sender_id']}]: ") - 20, 0
    )
    wrapped_message = textwrap.fill(message["message"], wrap_width)
    return f"{formatted_timestamp} [{message['sender_id']}]: {wrapped_message}\n\n"

def process_initial_world_state(message):
    header_buffer = Buffer(
        content=f"{message['world_name']}\n{message['world_description']}"
    )
    menu_items = {}
    menu_items["All Events"] = {"buffer": Buffer(), "event_types": []}
    menu_items["User Interactions"] = {"buffer": Buffer(), "event_types": []}

    # Specific for the podcast world TODO: generalize moving to a configuration file the specifics of the world
    if message["world_type"] == "PodcastWorld":
        menu_items["Podcast Room"] = {
            "buffer": Buffer(),
            "event_types": ["agent_speaks_into_microphone"],
        }

    for el in message["all_entities"]:
        if el["entity_type"] == "AGENT":
            menu_items[el["name"] + " Thoughts"] = {
                "buffer": Buffer(),
                "id": el["id"],
                "event_types": ["agent_thought_prompt", "agent_thought_output"],
            }
        elif el["entity_type"] == "OBJECT":
            menu_items[el["name"] + " Events"] = {
                "buffer": Buffer(),
                "id": el["id"],
                "event_types": [],
            }
            # for event in el["subscribed_events"]:
            #     self.menu_items[el["name"]+" Events"]["event_types"].append(event["event_type"])
    
    return header_buffer, menu_items