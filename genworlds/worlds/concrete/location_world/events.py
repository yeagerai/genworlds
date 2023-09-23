from genworlds.events.base_event import BaseEvent


class AgentMovesToNewLocation(BaseEvent):
    event_type = "agent_moves_to_new_location"
    description = "Agent moves to a new location in the world."
    destination_location: str
