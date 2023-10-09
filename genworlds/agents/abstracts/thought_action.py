from typing import Dict, Tuple
from genworlds.events.abstracts.action import AbstractAction
from genworlds.agents.abstracts.thought import AbstractThought


class ThoughtAction(AbstractAction):
    """
    Abstract interface class for a Thought Action.

    This includes the list of thoughts required to fill the parameters of the trigger event.
    """

    # {parameter_name: [thought_class, run_dict]}
    required_thoughts: Dict[str, Tuple[AbstractThought, dict]]

    # in the __call__ method after executing the action you must clean the state
    # with self.host_object.state_manager.state.other_thoughts_filled_parameters = {}
