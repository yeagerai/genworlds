# defines state
# defines state manager
# defines action planner
# defines agent

from typing import List
from genworlds.agents.abstracts.agent import AbstractAgent
from genworlds.agents.concrete.basic_assistant.state_manager import BasicAssistantStateManager
from genworlds.agents.concrete.basic_assistant.action_planner import BasicAssistantActionPlanner
from genworlds.events.abstracts.action import AbstractAction
from genworlds.agents.concrete.basic_assistant.actions import (
    UpdateAgentAvailableEntities, 
    UpdateAgentAvailableActionSchemas
)

class BasicAssistant(AbstractAgent):
    def __init__(self, name: str, id: str, description: str, host_world_id: str = None, actions: List[type[AbstractAction]] = []):
        
        state_manager = BasicAssistantStateManager(self, None)
        action_planner = BasicAssistantActionPlanner(None, None, None)

        actions.append(UpdateAgentAvailableEntities(host_object=self))
        actions.append(UpdateAgentAvailableActionSchemas(host_object=self))
        
        super().__init__(name, id, description, state_manager, action_planner, host_world_id, actions)