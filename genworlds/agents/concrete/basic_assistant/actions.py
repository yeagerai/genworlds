import json
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.action import AbstractAction
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.worlds.concrete.base.actions import (
    WorldSendsAvailableEntitiesEvent,
    WorldSendsAvailableActionSchemasEvent,
)


class UpdateAgentAvailableEntities(AbstractAction):
    trigger_event_class = WorldSendsAvailableEntitiesEvent
    description = "Update the available entities in the agent's state."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: WorldSendsAvailableEntitiesEvent):
        self.host_object.state_manager.state.available_entities = (
            event.available_entities
        )


class UpdateAgentAvailableActionSchemas(AbstractAction):
    trigger_event_class = WorldSendsAvailableActionSchemasEvent
    description = "Update the available action schemas in the agent's state."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: WorldSendsAvailableActionSchemasEvent):
        self.host_object.state_manager.state.available_action_schemas = (
            event.available_action_schemas
        )


class AgentWantsToSleepEvent(AbstractEvent):
    event_type = "agent_wants_to_sleep"
    description = "The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID."


class AgentGoesToSleepEvent(AbstractEvent):
    event_type = "agent_goes_to_sleep"
    description = "The agent is waiting."


class AgentGoesToSleep(AbstractAction):
    trigger_event_class = AgentWantsToSleepEvent
    description = "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentWantsToSleepEvent):
        self.host_object.state_manager.state.is_asleep = True
        self.host_object.state_manager.state.plan = []
        self.host_object.send_event(
            AgentGoesToSleepEvent(sender_id=self.host_object.id, target_id=None)
        )
        print("Agent goes to sleep...")


class WildCardEvent(AbstractEvent):
    event_type = "*"
    description = "This event is used as a master listener for all events."


class AgentListensEvents(AbstractAction):
    trigger_event_class = WildCardEvent
    description = "The agent listens to all the events and stores them in his memory."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: dict):
        if (
            event["target_id"] == self.host_object.id
            or event["target_id"] == None
            or event["sender_id"] == self.host_object.id
        ):
            if (
                event["event_type"]
                not in self.host_object.state_manager.state.memory_ignored_event_types
            ):
                self.host_object.state_manager.memory.add_event(
                    json.dumps(event), summarize=False
                )  # takes time
            if (
                event["event_type"]
                in self.host_object.state_manager.state.wakeup_event_types
            ):
                self.host_object.state_manager.state.is_asleep = False
                print("Agent is waking up...")


class AgentSpeaksWithUserTriggerEvent(AbstractEvent):
    event_type = "agent_speaks_with_user_trigger_event"
    description = "An agent speaks with the user."
    message: str


class AgentSpeaksWithUserEvent(AbstractEvent):
    event_type = "agent_speaks_with_user_event"
    description = "An agent speaks with the user."
    message: str


class AgentSpeaksWithUser(AbstractAction):
    trigger_event_class = AgentSpeaksWithUserTriggerEvent
    description = "An agent speaks with the user."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentSpeaksWithUserTriggerEvent):
        self.host_object.send_event(
            AgentSpeaksWithUserEvent(
                sender_id=self.host_object.id,
                target_id=event.target_id,
                message=event.message,
            )
        )


class AgentSpeaksWithAgentEvent(AbstractEvent):
    event_type = "agent_speaks_with_agent_event"
    description = "An agent speaks with another agent."
    message: str


class AgentSpeaksWithAgent(AbstractAction):
    trigger_event_class = AgentSpeaksWithAgentEvent
    description = "An agent speaks with another agent."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentSpeaksWithAgentEvent):
        self.host_object.send_event(event)
