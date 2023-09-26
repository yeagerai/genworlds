from typing import List, Type
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.events.abstracts.action import AbstractAction
from genworlds.agents.abstracts.thought import AbstractThought


class ThoughtAction(AbstractAction):
    """
    Abstract interface class for a Thought Action.

    This includes the list of thoughts required to fill the parameters of the trigger event.
    """

    required_thoughts: List[AbstractThought]

    def __init__(self, trigger_event: Type[AbstractEvent]):
        super().__init__(trigger_event)
