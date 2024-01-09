from functools import wraps
from typing import Callable, Any
from datetime import datetime

from genworlds.core.types import Event, WorldState
from genworlds.core.utils import apply_nested_modifications
from genworlds.core.comms import event_mult

def action(action_func: Callable):
    """
    Decorator that transforms a function into a world action.
    """
    @wraps(action_func)
    async def wrapper(entity_type: str, id: str, world_state_atom: WorldState, internal_entity_state: Any, new_event: Event):
        assert callable(action_func), "Action must be a function"

        updated_state = await action_func(internal_entity_state, new_event)
        updated_state_dict = updated_state._asdict()
        source_atom_dict = world_state_atom._asdict()
        apply_nested_modifications(source_atom_dict,updated_state_dict)

        if source_atom_dict != world_state_atom._asdict():
            request_world_modification_event = Event(
                sender_id=id,
                target_id=world_state_atom.id,
                created_at=datetime.now(),
                event_type="request_world_modification_event",
                data={"actual_modification_dict":source_atom_dict,
                      "source_atom_dict":world_state_atom._asdict()}
            )
            await event_mult.broadcast(request_world_modification_event)

    return wrapper
