import json
from datetime import datetime

from genworlds.core.types import Event, WorldState

def stringify_event(event: Event) -> str:
    event_dict = event._asdict()
    if isinstance(event.created_at, datetime):
        event_dict['created_at'] = event.created_at.strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps(event_dict)

def can_apply_modification(source_atom: WorldState, current_atom: WorldState, actual_modification: WorldState):
    source_atom = source_atom._asdict()
    current_atom = current_atom._asdict()
    actual_modification = actual_modification._asdict()

    for key in actual_modification:
        if key in current_atom and key in source_atom:
            if source_atom[key] != current_atom[key]:
                return False
    return True

def apply_nested_modifications(main_dict, modifications_dict):
    def apply_modifications_recursively(current_dict, key, value):
        if key in current_dict:
            current_dict[key] = value
        else:
            for k, v in current_dict.items():
                if isinstance(v, dict):
                    apply_modifications_recursively(v, key, value)

    for mod_key, mod_value in modifications_dict.items():
        apply_modifications_recursively(main_dict, mod_key, mod_value)
