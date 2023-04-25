from yeager_core.events.base_event import Event


class MoveAgentToNewPositionEvent(Event):
    event_type = "move_agent_to_new_position"
    description = "Move an agent to a new position."
    agent_id: str
    new_position: str
