from prompt_toolkit.key_binding import KeyBindings

def init_keybindings(menu_items, menu_highlighted_index, menu_buffer):
    kb = KeyBindings()

    @kb.add("c-c", eager=True)
    def exit_app(event):
        event.app.exit()

    @kb.add("up")
    def navigate_up(event):
        if menu_highlighted_index > 0:
            menu_highlighted_index -= 1
        menu_buffer.text = _create_menu_text()

    @kb.add("down")
    def navigate_down(event):
        if menu_highlighted_index < len(menu_items) - 1:
            menu_highlighted_index += 1
        menu_buffer.text = _create_menu_text()

    @kb.add("c-s")
    def select_item(event):
        _handle_menu_selection()
    return kb

def _create_menu_text(menu_items, menu_highlighted_index):
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

def _handle_menu_selection(self):
    # TODO: switch chat window based on menu selection
    pass