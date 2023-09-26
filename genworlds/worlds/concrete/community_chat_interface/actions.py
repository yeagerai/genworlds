import json
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.events.abstracts.action import AbstractAction


class UserRequestsScreensToWorldEvent(AbstractEvent):
    event_type = "user_requests_screens_to_world"
    description = "Agent moves to a new location in the world."


class WorldSendsScreensToUserEvent(AbstractEvent):
    event_type = "world_sends_screens_to_user"
    description = "Agent moves to a new location in the world."
    screens_config: dict


class WorldSendsScreensToUser(AbstractAction):
    trigger_event_class = UserRequestsScreensToWorldEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: UserRequestsScreensToWorldEvent):
        with open(self.host_object.screens_config_path) as f:
            screens_config = json.load(f)

        event = WorldSendsScreensToUserEvent(
            sender_id=self.host_object.id,
            screens_config=screens_config,
        )
        self.host_object.send_event(event)
