from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.action import AbstractAction
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.worlds.concrete.base.actions import (
    WorldSendsAvailableEntitiesEvent,
    WorldSendsAvailableActionSchemasEvent,
)


class UpdateAgentAvailableEntities(AbstractAction):
    trigger_event_class = WorldSendsAvailableEntitiesEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: WorldSendsAvailableEntitiesEvent):
        self.host_object.state_manager.state.available_entities = (
            event.available_entities
        )


class UpdateAgentAvailableActionSchemas(AbstractAction):
    trigger_event_class = WorldSendsAvailableActionSchemasEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: WorldSendsAvailableActionSchemasEvent):
        self.host_object.state_manager.state.available_action_schemas = (
            event.available_action_schemas
        )

class AgentWantsToSleep(AbstractEvent):
    event_type = "agent_wants_to_sleep"
    description = "The agent wants to sleep. He has to wait for new events."

class AgentGoesToSleep(AbstractAction):
    trigger_event_class = AgentWantsToSleep

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentWantsToSleep):
        self.host_object.state_manager.state.is_asleep = True
        print("Agent goes to sleep...")

class WildCardEvent(AbstractEvent):
    event_type = "*"
    description = "This event is used as a master listener for all events."
class AgentListensEvents(AbstractAction):
    trigger_event_class = WildCardEvent

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AbstractEvent):
        if event.target_id == self.host_object.id or event.target_id == None:
            self.host_object.state_manager.memory.add_event(event, summarize=True)
            if event.event_type in self.host_object.state_manager.state.wakeup_event_types:
                self.host_object.state_manager.state.is_asleep = False
                print("Agent is waking up...")