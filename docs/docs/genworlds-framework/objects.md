---
sidebar_position: 3
---

# Objects

Objects are the simplest GenWorlds event listener. Every object defines a unique set actions (usually deterministic), and is reactive. So listens to world events and reacts to them with its actions. Thus, enabling agents to accomplish specific tasks and work together in a dynamic environment.

All objects must inherit from the `AbstractObject` interface class:

```python
class AbstractObject(SimulationSocketEventHandler):
"""
A Class representing a generic object in the simulation.
"""

def __init__(
    self,
    name: str,
    id: str,
    description: str,
    host_world_id: str = None,
    actions: List[Type[AbstractAction]] = [],
):
    self.host_world_id = host_world_id
    self.name = name
    self.description = description

    super().__init__(id=id, actions=actions)
```

In particular, Worlds and Agents are also objects.

Objects in GenWorlds are versatile and can be subclassed to achieve varying purposes, such as 'token bearers' or 'tools'. For instance, a 'token bearer' like a microphone in a podcast studio, can be passed among agents, fostering a collaborative environment. The agent currently holding the token (or the microphone) gains the ability to perform unique actions, like speaking to the audience. This mechanism introduces the notion of shared resources and cooperative interactions, reinforcing that objects aren't confined to one agent, but can be easily exchanged and used throughout the collective.

A 'tool', on the other hand, can execute specific functions such as calling external APIs, running complex calculations, or triggering unique events in the world.

This way, by defining various objects and mapping them to specific events, you can design rich and complex interactions in the GenWorlds environment.

For instance a simple microphone object can be defined as follows:

```python
class Microphone(AbstractObject):
    def __init__(self, id:str, holder_agent_id: str):
        self.holder_agent_id = holder_agent_id
        actions = [SendMicrophoneToAgent(host_object=self), AgentSpeaksIntoMicrophone(host_object=self)]

        super().__init__(name="Microphone", 
                         id=id, 
                         description="""A podcast microphone that allows the holder of it to speak to the
audience. The speaker can choose to make a statement, ask a question, respond
to a question, or make a joke.""", 
                         actions=actions
                         )

```

But as we explained before in the actions section of this docs, entities are mainly defined by their actions. So let's take a look at the actions that this microphone object can perform:

```python
class SendMicrophoneToAgentEvent(AbstractEvent):
    event_type = "send_microphone_to_agent_event"
    description = "An agent sends the microphone to another agent."

class NewHolderOfMicrophoneEvent(AbstractEvent):
    event_type = "new_holder_of_microphone_event"
    description = "Event that states who is the new holder of the microphone."
    new_holder_id:str

class SendMicrophoneToAgent(AbstractAction):
    trigger_event_class = SendMicrophoneToAgentEvent
    description = "An agent sends the microphone to another agent."
    
    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)
    
    def __call__(self, event: SendMicrophoneToAgentEvent):
        self.host_object.holder_agent_id = event.target_id
        event = NewHolderOfMicrophoneEvent(
            sender_id=self.host_object.id,
            target_id=self.host_object.holder_agent_id
            new_holder=self.host_object.holder_agent_id
        )
        self.host_object.send_event(event)
```

This is the action that makes the microphone object reactive. It listens to the `SendMicrophoneToAgentEvent` event, and when it is triggered, it changes the `holder_agent_id` attribute of the microphone object to the `target_id` of the event. Then it sends a `NewHolderOfMicrophoneEvent` event to the world, stating who is the new holder of the microphone.

But microphones are not only for passing around. They are also for speaking into them. So let's take a look at the `AgentSpeaksIntoMicrophone` action:

```python
class AgentSpeaksIntoMicrophoneTriggerEvent(AbstractEvent):
    event_type = "agent_speaks_into_microphone_trigger_event"
    description = "An agent sends the microphone to another agent."
    message:str
        
class AgentSpeaksIntoMicrophoneEvent(AbstractEvent):
    event_type = "agent_speaks_into_microphone_event"
    description = "Event that states who is the new holder of the microphone."
    message:str

class NotAllowedToSpeakEvent(AbstractEvent):
    event_type = "not_allowed_to_speak_event"
    description = "The agent who is trying to speak into the microphone is not allowed."
    message:str

class AgentSpeaksIntoMicrophone(AbstractAction):
    trigger_event_class = SendMicrophoneToAgentEvent
    description = "An agent sends the microphone to another agent."
    
    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)
    
    def __call__(self, event: AgentSpeaksIntoMicrophoneTriggerEvent):
        if self.host_object.holder_agent_id == event.sender_id:
            event = AgentSpeaksIntoMicrophoneEvent(
                sender_id=event.sender_id,
                target_id=self.host_object.id,
                message=event.message,
            )
            self.host_object.send_event(event)
        else:
            event = NotAllowedToSpeakEvent(
                sender_id=self.host_object.id,
                target_id=event.sender_id,
                message=f"You are not allowed to speak into the microphone as you are not the current holder of the microphone, keep waiting for now."
            )
            self.host_object.send_event(event)
```

This action listens to the `AgentSpeaksIntoMicrophoneTriggerEvent` event, and when it is triggered, it checks if the sender of the event is the current holder of the microphone. If it is, then it sends a `AgentSpeaksIntoMicrophoneEvent` event to the world, stating that the agent is speaking into the microphone. If it is not, then it sends a `NotAllowedToSpeakEvent` event to the world, stating that the agent is not allowed to speak into the microphone. Thus, converting the microphone in a token bearer object for coordinating communication between agents.
