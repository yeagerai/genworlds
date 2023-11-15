import traceback
from time import sleep
import threading
from typing import List, Type

from genworlds.agents.utils.validate_action import validate_action
from genworlds.agents.abstracts.action_planner import AbstractActionPlanner
from genworlds.agents.abstracts.state_manager import AbstractStateManager
from genworlds.events.abstracts.action import AbstractAction
from genworlds.objects.abstracts.object import AbstractObject


class AbstractAgent(AbstractObject):
    """Abstract interface class for an Agent.

    This class represents an abstract agent that can think and perform actions
    within a simulation environment.
    """

    def __init__(
        self,
        name: str,
        id: str,
        description: str,
        state_manager: Type[AbstractStateManager],
        action_planner: Type[AbstractActionPlanner],
        host_world_id: str = None,
        actions: List[type[AbstractAction]] = [],
    ):
        self.action_planner = action_planner
        self.state_manager = state_manager
        super().__init__(name, id, description, host_world_id, actions)

    def think_n_do(self):
        """Continuously plans and executes actions based on the agent's state."""
        while True:
            try:
                if self.state_manager.state.is_asleep:
                    sleep(1)
                    continue
                else:
                    sleep(
                        0.5
                    )  # actions that its output take over 0.5 secs have to implement a sleep in the action before finishing
                    state = self.state_manager.get_updated_state()
                    sleep(0.5)
                    action_schema, trigger_event = self.action_planner.plan_next_action(
                        state
                    )

                    if action_schema.startswith(self.id):
                        selected_action = [
                            action
                            for action in self.actions
                            if action.action_schema[0] == action_schema
                        ][0]
                        selected_action(trigger_event)
                    else:
                        self.send_event(trigger_event)
            except Exception as e:
                print(f"Error in think_n_do: {e}")
                traceback.print_exc()

    def launch(self):
        """Launches the agent by starting the websocket and thinking threads."""
        self.launch_websocket_thread()
        sleep(0.1)
        thinking_thread = threading.Thread(
            target=self.think_n_do,
            name=f"Agent {self.state_manager.state.id} Thinking Thread",
            daemon=True,
        )
        thinking_thread.start()
