---
sidebar_position: 1
---

# Actions and events

The GenWorlds framework is built around the concept of asynchronous communication, and thus event based communication. We think that is the natural way for autonomous AI agents to communicate with other entities because you never know when an agent is going to finish a task, or how it would react to a specific event and change its plan.

So to implement event based communication, we decided to use websockets as the main communication channel. This allows us to have a very simple and flexible communication protocol, and also allows us to easily integrate with other systems such as backends or webapps.

Now talking more specifically about how GenWorlds implements this event-based communication is through the concepts of events and actions.

## Events

Events are mainly pieces of information that are sent from one entity to the world socket server, and thus update the state of the world. You can see it as small `json` payloads that inform the world about something that happened. We use pydantic BaseModels to define the structure of the events, so mainly all events must follow our `AbstractEvent` interface.

```python
class AbstractEvent(ABC, BaseModel):
    event_type: str
    description: str
    summary: Optional[str]
    created_at: datetime = Field(default_factory=datetime.now)
    sender_id: str
    target_id: Optional[str]
```

As you can see, all events must have a `event_type` and a `description`. The `event_type` is a string that identifies the type of event, and the `description` is a human readable description of the event. The `summary` is an optional field that can be used to give a short summary of the event. The `created_at` field is the timestamp of when the event was created. The `sender_id` is the id of the entity that sent the event, and the `target_id` is the id of the entity that the event is targeted to. This is useful for example when an agent wants to speak to another agent.

Here is a possible implementation of this kind of event:

```python
class AgentSpeaksWithAgentEvent(AbstractEvent):
    event_type = "agent_speaks_with_agent_event"
    description = "An agent speaks with another agent."
    message: str
```

Then at runtime we must define the `sender_id`, the `target_id` and the `message`. That's where actions come into play.

## Actions

Actions are the main way to define how an entity reacts to an event. We have to remember that all entities are in fact event-listeners connected to a socket server. Actions are defined by a `trigger_event_class` which is the event that triggers the action, and a `__call__` method that is called when the action is triggered. The `__call__` method receives the event that triggered the action as a parameter.

Most of the time, actions also send events to the world socket server, and thus update the state of the world, after executing the routine of the `__call__` method. Here is an example of an action that is used in the basic utility layer of GenWorlds to enable user-agent communication:

```python
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
```

As you can see, the `AgentSpeaksWithUser` action is defined by a `trigger_event_class` which is the event that triggers the action. In this case the `AgentSpeaksWithUserTriggerEvent` is triggered by the agent when it wants to speak with the user. The action then sends the `AgentSpeaksWithUserEvent` to the user with the message. Remember that all this communication happens asynchronously through the socket server where every entity (world included) has its own event-listener.

## Action based development

Actions are the keystone of the framework. So as a developer you have to start thinking about what actions you want to define for your entities. For example, if you want to define a `Microphone` object, you must think about what actions you want to define for it. For example, you can define an action that is triggered when an agent speaks into the microphone, and then the action sends an event to the world socket server with the message. Then you can define an action that is triggered when an agent passes the microphone to another agent, and then the action sends an event to the world socket server with the new agent that is holding the microphone. And so on.
