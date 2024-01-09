from typing import Callable
import asyncio

from genworlds.core.types import EntityState, Event, WorldState
from genworlds.core.comms import event_mult
from genworlds.core.utils import can_apply_modification

world_state_dict = {} # Singleton
def get_world_state_dict():
    return world_state_dict

def entity_updates_internal_state(entity_state: EntityState, event: Event) -> EntityState:
    if entity_state.custom_state_updaters:
        return entity_state.custom_state_updaters(entity_state, event)
    return entity_state

def entity_chooses_action(entity_state: EntityState, new_event: Event) -> Callable:
    return entity_state.actions.get(new_event.event_type)

async def entity(id: str):
    entity_chan = asyncio.Queue()
    event_mult.subscribe(entity_chan)

    while True:
        new_event:Event = await entity_chan.get()
        try:
            if new_event.target_id in [id, "*"]:
                world_state = WorldState(**get_world_state_dict())
                internal_object_state = world_state.entity_states[id]
                new_internal_state = entity_updates_internal_state(internal_object_state, new_event)
                chosen_action = entity_chooses_action(new_internal_state, new_event)

                if callable(chosen_action):
                    await chosen_action("entity", id, world_state, new_internal_state, new_event)
        except AttributeError:
            continue


async def world(id: str, initial_world_state: WorldState):
    global world_state_dict
    world_state_dict = initial_world_state._asdict()
    world_state = WorldState(**world_state_dict)
    world_chan = asyncio.Queue()
    event_mult.subscribe(world_chan)
    while True:
        new_event:Event = await world_chan.get()
        try:
            if new_event.target_id in [id, "*"]:
                if new_event.event_type == "request_world_modification_event" and can_apply_modification(new_event.data["source_atom_dict"], world_state_dict, new_event.data["actual_modification_dict"]):
                    world_state_dict = new_event.data["actual_modification_dict"] # the only line that can modify the world_state_dict singleton
                    world_state = WorldState(**world_state_dict)
                elif new_event.event_type == "request_world_state":
                    await event_mult.broadcast(Event(world_state))
                else:
                    new_internal_state = entity_updates_internal_state(world_state, new_event)
                    chosen_action = entity_chooses_action(new_internal_state, new_event)

                    if callable(chosen_action):
                        await chosen_action("world", id, world_state, new_internal_state, new_event)
        except AttributeError:
            continue