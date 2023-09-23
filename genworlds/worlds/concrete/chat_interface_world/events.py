from genworlds.events.base_event import BaseEvent


class UserRequestsScreensToWorld(BaseEvent):
    event_type = "user_requests_screens_to_world"
    description = "Agent moves to a new location in the world."


class WorldSendsScreensToUser(BaseEvent):
    event_type = "world_sends_screens_to_user"
    description = "Agent moves to a new location in the world."
    screens_config: dict
