from yeager_core.events.base_event import Event
from yeager_core.objects.base_object import BaseObject


class AddObjectToWorldEvent(Event):
    event_type = "add_object_to_world"
    description = "Add an object to the world."
    object: BaseObject
