import json
from datetime import datetime
import websockets

from genworlds.core.types import Event, WorldState

def convert_event_to_serializable_objs(obj):
    if callable(obj):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(obj, dict):
        return {k: convert_event_to_serializable_objs(v) for k, v in obj.items()}
    elif hasattr(obj, "_asdict"):
        return {k: convert_event_to_serializable_objs(v) for k, v in obj._asdict().items()}
    elif isinstance(obj, list):
        return [convert_event_to_serializable_objs(v) for v in obj]
    else:
        return obj

def stringify_event(event) -> str:
    return json.dumps(convert_event_to_serializable_objs(event))

async def trigger_simulation(uri, event: Event):
    async with websockets.connect(uri) as websocket:
        await websocket.send(stringify_event(event))


def can_apply_modification(source_atom: WorldState, current_atom: WorldState, actual_modification: WorldState):

    for key in actual_modification:
        if key in current_atom and key in source_atom:
            if source_atom[key] != current_atom[key]:
                return False
    return True

def apply_nested_modifications(main_dict, path, new_sub_dict):
    def get_nested_dict(dct, path):
        for key in path:
            dct = dct[key]
        return dct

    parent_dict = get_nested_dict(main_dict, path[:-1])
    parent_dict[path[-1]] = new_sub_dict
