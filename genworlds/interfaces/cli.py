import threading

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, VSplit, Window, WindowAlign
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style

from genworlds.sockets.world_socket_client import WorldSocketClient

def process_agent_message(message):
    return f"{message['created_at']} [{message['sender_id']}]: {message['message']}\n"

def process_event(ws_json_message):
    if ws_json_message['event_type'] == 'agent_speaks_into_microphone':
        chat_buffer.text += process_agent_message(ws_json_message)

ws_client = WorldSocketClient(process_event)



chat_room_name = "Chat Room"
chat_room_description = "This is a chat room, where you can chat with other agents"
agents = [
    {
        "agent_name":"Agent 1",
        "agent_description": "This is agent 1",
    },
    {
        "agent_name":"Agent 2",
        "agent_description": "This is agent 2",
    },
]

# Define the menu items
agent_items = [(agent["agent_name"], f"item-{i+2}") for i,agent in enumerate(agents)]

menu_items = [
    (chat_room_name, "item-1"),
    *agent_items,]

# Initialize buffers and menu index
chat_buffer = Buffer()
prompt_buffer = Buffer()
menu_highlighted_index = 0

# Update text in left buffer when menu selection is made
def handle_menu_selection():
    selected_item = menu_items[menu_highlighted_index][0]
    chat_buffer.text = f"Selected: {selected_item}"

# Update text in left buffer when text in prompt changes
def handle_prompt_text_changed(_):
    chat_buffer.text = f"Prompt: {prompt_buffer.text}"

# Construct formatted text for menu items
def create_menu_text():
    menu_text = []
    for i, (item, _) in enumerate(menu_items):
        if i == menu_highlighted_index:
            style_class = "class:menu.highlighted"
            menu_text.append((style_class, "> "))
            menu_text.append((style_class, item))
            menu_text.append((style_class, "\n"))
        else:
            style_class = "class:menu.normal"
            menu_text.append((style_class, "  "))
            menu_text.append((style_class, item))
            menu_text.append((style_class, "\n"))
    return menu_text


# Create menu content control
menu_content = FormattedTextControl(create_menu_text)

header = Window(height=3, content=FormattedTextControl([("class:title", f" {chat_room_name}\n"),
                                                       ("class:title", f" {chat_room_description}\n")]), align=WindowAlign.LEFT)

switch_chat_menu = Window(content=menu_content, width=D.exact(15), style="class:menu", wrap_lines=False)
chat = Window(BufferControl(buffer=chat_buffer))
chat_user_input = Window(height=3, content=BufferControl(buffer=prompt_buffer), style="class:prompt")
footer = Window(height=2, content=FormattedTextControl([("class:title", "The default 🧬🌍 GenWorlds interface\n"),
                                                       ("class:title", "Press [Ctrl-S] to select chat. | Press [Ctrl-C] to quit.")]), align=WindowAlign.CENTER)

root_container = HSplit(
    [
        header,
        Window(height=1, char="-", style="class:line"),
        VSplit([
            switch_chat_menu,
            Window(width=1, char="|", style="class:line"),
            chat,
        ]),
        Window(height=1, char="-", style="class:line"),
        chat_user_input,
        Window(height=1, char="-", style="class:line"),
        footer,
    ]
)


kb = KeyBindings()

@kb.add("c-c", eager=True)
def exit_app(event):
    event.app.exit()

@kb.add("up")
def navigate_up(event):
    global menu_highlighted_index
    if menu_highlighted_index > 0:
        menu_highlighted_index -= 1
    menu_content.text = create_menu_text()

@kb.add("down")
def navigate_down(event):
    global menu_highlighted_index
    if menu_highlighted_index < len(menu_items) - 1:
        menu_highlighted_index += 1
    menu_content.text = create_menu_text()

@kb.add("c-s")
def select_item(event):
    handle_menu_selection()

# Handle text changes in prompt
prompt_buffer.on_text_changed += handle_prompt_text_changed

style = Style([
    ('menu.highlighted', 'fg:white bg:grey'),
    ('menu.normal', 'fg:black'),
])

# Define application
application = Application(
    layout=Layout(root_container, focused_element=prompt_buffer),
    key_bindings=kb,
    mouse_support=True,
    full_screen=True,
    style=style,
)

def run():
    threading.Thread(
        target=ws_client.websocket.run_forever,
        name=f"CLI Chat Room Thread",
        daemon=True,
    ).start()
    application.run(),
    

if __name__ == "__main__":
    run()
