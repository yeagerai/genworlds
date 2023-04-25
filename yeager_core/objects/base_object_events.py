from typing import List
from yeager_core.events.base_event import Event


class GetObjectInfoEvent(Event):
    event_type = "get_object_info"
    description = "Get info about an object."
    object_name: str
    object_id: str
    object_description: str
    possible_actions: List[str]
