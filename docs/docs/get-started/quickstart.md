---
sidebar_position: 2
---

# Quickstart

Whether you're a creator dreaming up new simulated worlds, or a developer looking to enhance the GenWorlds framework and tools, our quickstart guides have got you covered.

:::tip Info

GenWorlds utilizes GPT-4, which is currently accessible to those who have made at least one successful payment through `https://platform.openai.com/`.

:::

## Quickstart: Dive into GenWorlds

Welcome! Get ready to create your first multi-agent system with GenWorlds. Let’s start:

### Step 1: Install GenWorlds

```bash
pip install genworlds
```

### Step 2: Create Your First World

Generate your initial world (by now empty), where agents and objects will live.

```python
from genworlds.worlds.concrete.base.world import BaseWorld

# Define the World
hello_world = BaseWorld(
    name="Hello World",
    description="A world for testing the library.",
)

# Launch the World
hello_world.launch()
```

```output
INFO:numexpr.utils:NumExpr defaulting to 8 threads.
INFO:     Started server process [25828]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:7456 (Press CTRL+C to quit)
INFO:     ('127.0.0.1', 64237) - "WebSocket /ws" [accepted]
INFO:     connection open
INFO:websocket:Websocket connected
[4816cdfb-74ab-42a4-9c2e-7d82c55c8886 Thread] Connected to world socket server ws://127.0.0.1:7456/ws
INFO:4816cdfb-74ab-42a4-9c2e-7d82c55c8886 Thread:Connected to world socket server ws://127.0.0.1:7456/ws
```

### Step 3: Add Agents

Insert one agent (a basic assistant) into your world and define their characteristics and abilities. This basic assistant is an autonomous AI Agent.

```python
from genworlds.agents.concrete.basic_assistant.utils import generate_basic_assistant
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent

description = """Agent that helps the user to answer questions."""

# Generate a basic assistant (you have to provide the openai_api_key)
agent1 = generate_basic_assistant(
    agent_name="agent1",
    description=description,
    openai_api_key=openai_api_key
)

# Add wakeup events to the agents so you can interact with the agent after is sleeping
agent1.add_wakeup_event(event_class=UserSpeaksWithAgentEvent)

## Attach the agent to the World
hello_world.add_agent(agent1)
```

```output
INFO:     ('127.0.0.1', 64255) - "WebSocket /ws" [accepted]
INFO:     connection open
INFO:websocket:Websocket connected
[agent1 Thread] Connected to world socket server ws://127.0.0.1:7456/ws
INFO:agent1 Thread:Connected to world socket server ws://127.0.0.1:7456/ws
...
...

> Finished chain.
{"event_type": "agent_wants_to_sleep", "description": "The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.", "summary": "Agent1 is waiting for a new question from the user.", "created_at": "2022-01-01T00:00:00+00:00", "sender_id": "agent1", "target_id": "agent1"}
Agent goes to sleep...
{"event_type": "agent_goes_to_sleep", "description": "The agent goes to sleep.", "summary": null, "created_at": "2023-10-03T15:03:45.741527", "sender_id": "agent1", "target_id": null}
```

Here you will see a long output till the agents go to sleep.

If you use `.env` files to store your `openai_api_key`, you can load it with:

```python
import os
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
```

### Step 4: Specify Actions and Events of an Object

The most important step to define world entities, or objects more in particular is defining its actions. The actions are the functions that can be triggered through the socket usually by agents. So, when an agent triggers an action, the action will perform some logic and will send an event to the socket. The event will be received by the agent that triggered the action and by the other agents that are subscribed to it.

```python
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.events.abstracts.action import AbstractAction
from genworlds.objects.abstracts.object import AbstractObject

# Create two events and one action
# Event that the agent will use to ask for the sum of two numbers
class AgentWantsToAddTwoNumbers(AbstractEvent):
    event_type = "agent_wants_to_add_two_numbers_event"
    description = "Sends two float numbers to be added in a deterministic way."
    number1 : float
    number2 : float

# Event that the SimpleCalculator will send to the agent with the sum of the two numbers
class SendAddedNumbersToAgent(AbstractEvent):
    event_type = "send_added_numbers_to_agent_event"
    description = "Sends the requested deterministic sum of the two numbers to the agent"
    sum : float

# The action that will be triggered by the event and will perform the addition of the two numbers
class AddTwoNumbers(AbstractAction):
    trigger_event_class = AgentWantsToAddTwoNumbers
    description = "Is used to add two float numbers in a deterministic way."
    
    def __init__(self, host_object: AbstractObject):
        self.host_object = host_object
    
    def __call__(self, event:AgentWantsToAddTwoNumbers):
        event = SendAddedNumbersToAgent(
            sender_id=self.host_object.id,
            target_id=event.sender_id,
            sum = event.number1 + event.number2,
        )
        self.host_object.send_event(event)
```

We all can agree that is a bit boilerplate for just adding two numbers, but this syntax is very useful when you want to create more complex actions that will require more logic.

### Step 5: Define the Object and attach the actions and events to it

Now we can create a `SimpleCalculator` object, and add the deterministic action `AddTwoNumbers` to it. So when an agent triggers this action, it will be adding two numbers in a deterministic way, not using any LLM. You can see it as an OpenAI Plugin.

```python
# Define the SimpleCalculator Class
class SimpleCalculator(AbstractObject):
    def __init__(self, id:str):
        actions = [AddTwoNumbers(host_object=self)]
        super().__init__(name="Simple Calculator", 
                         id=id, 
                         description="Object used to do some calculations such as adding two numbers.",
                         actions=actions
                         )

# Instantiate the SimpleCalculator Class
simple_calculator = SimpleCalculator(id="simple_calculator")

# Incorporate the simple_calculator object into the World
hello_world.add_object(simple_calculator)
```

```output
INFO:     ('127.0.0.1', 64361) - "WebSocket /ws" [accepted]
INFO:     connection open
INFO:websocket:Websocket connected
[simple_calculator Thread] Connected to world socket server ws://127.0.0.1:7456/ws
INFO:simple_calculator Thread:Connected to world socket server ws://127.0.0.1:7456/ws
```

### Step 6: Interact with World entities

Now we want to wake up one of the agents and send a message so it can use the `SimpleCalculator` object. That is probably the easiest way of interacting with an agent. First we are going to instantiate a `TestUser`.

```python
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent
from genworlds.utils.test_user import TestUser

# Create a Testing User
test_user = TestUser()
```

```output
INFO:     ('127.0.0.1', 64375) - "WebSocket /ws" [accepted]
INFO:     connection open
INFO:websocket:Websocket connected
[test_user Thread] Connected to world socket server ws://127.0.0.1:7456/ws
INFO:test_user Thread:Connected to world socket server ws://127.0.0.1:7456/ws
```

And now we can send a message to the agent.

```python
message_to_send = UserSpeaksWithAgentEvent(
    sender_id=test_user.id,
    message="Please add the numbers 2.45 and 6.78 and send me the result.", 
    target_id="agent1"
).json()

# Send the message to John
test_user.socket_client.send_message(message_to_send)
```

```output
{"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-03T15:34:31.224852", "sender_id": "test_user", "target_id": "agent1", "message": "Please add the numbers 2.45 and 6.78 and send me the result."}
Agent is waking up...
...
...
> Finished chain.
{"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-03T15:35:21.921470", "sender_id": "agent1", "target_id": null, "message": "The result of adding 2.45 and 6.78 is 9.23."}
...
...
> Finished chain.
Agent goes to sleep...
{"event_type": "agent_goes_to_sleep", "description": "The agent goes to sleep.", "summary": null, "created_at": "2023-10-03T15:35:39.997321", "sender_id": "agent1", "target_id": null}
```

## Step 7: Explore More

Now, delve into more advanced concepts with the following tutorials:

- [Foundational RAG World](https://genworlds.com/) An example of a RAG (Retrieval Augmented Generation) World that can be used as a foundational piece from where to expand and create a knowledge source of your projects. Here you will learn a lot about deterministic actions and objects.
- [Custom Q&A Agent](https://genworlds.com/) In this tutorial, you will learn how you can create custom autonomous agents that have multiple thoughts and how they get integrated into already existing worlds.

### Collaboration Methods

- [First-Steps](https://genworlds.com/) An example of a basic world, with two agents that cooperate to achieve a very simple task.
- [Token Bearer (Roundtable)](https://genworlds.com/) An example of a multi-agent system, where agents interact with each other speaking through a microphone, which is a token to communicate and to signal to the other Agents whose turn it is to perform an action.
