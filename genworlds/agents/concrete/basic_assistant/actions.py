from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.action import AbstractAction

from genworlds.worlds.concrete.base.actions import (
    WorldSendsAvailableEntitiesEvent, 
    WorldSendsAvailableActionSchemasEvent
)

class UpdateAgentAvailableEntities(AbstractAction):
    trigger_event_class = WorldSendsAvailableEntitiesEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)
    
    def __call__(self, event: WorldSendsAvailableEntitiesEvent):
        self.host_object.state_manager.state.available_entities = event.available_entities

class UpdateAgentAvailableActionSchemas(AbstractAction):
    trigger_event_class = WorldSendsAvailableActionSchemasEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)
    
    def __call__(self, event: WorldSendsAvailableActionSchemasEvent):
        self.host_object.state_manager.state.available_action_schemas = event.available_action_schemas