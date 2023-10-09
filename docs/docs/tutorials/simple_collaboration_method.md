---
sidebar_position: 1
---
# Simple Collaboration Method

:::tip Info

The information hereunder has been extracted from `https://github.com/yeagerai/genworlds/tree/main/use_cases/simple_collaboration_method`. There you have the `.ipynb` file and other supplementary resources.

:::

In this beginner's tutorial, we'll walk through creating a simple GenWorld from scratch. By the end, you'll have a basic understanding of how GenWorlds operates, setting the stage for more advanced use cases.

## Scenario Overview:

Imagine a world where two agents, "John" and "Matthew", work in tandem. John receives a request from a user to generate a random matrix and determine its determinant. John then uses a tool to craft this matrix, which he sends over to Matthew. Matthew, equipped with a different tool, calculates the determinant of the matrix John created. After doing so, Matthew sends back the result to John, who then delivers the original matrix and the determinant value to the user.

While this might sound like overkill for a simple task (since the LLM could probably do this in one go), the purpose is to demonstrate how different components of GenWorlds can interact.

## Step 1: Initial Set Up

Before diving into our world, we need a few basic utilities and configurations.


```python
from datetime import datetime
import threading
from typing import List
from time import sleep
import os
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
```

## Step 2: Crafting the World

Our world, named "Compute Matrix Determinant World", will initially be empty. We'll then populate it with agents and objects in subsequent steps.


```python
from genworlds.worlds.concrete.base.world import BaseWorld

# Define the World
CMD_world = BaseWorld(
    name="Compute Matrix Determinant World",
    description="A world where two agents interact to generate a matrix and compute its determinant.",
)
CMD_world.launch()
```

```output

    INFO:numexpr.utils:NumExpr defaulting to 8 threads.
    INFO:     Started server process [18964]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:7456 (Press CTRL+C to quit)
    INFO:     ('127.0.0.1', 56961) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [31m[72581673-a808-462f-b903-39d1ae4c9d2f Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:72581673-a808-462f-b903-39d1ae4c9d2f Thread:Connected to world socket server ws://127.0.0.1:7456/ws
```    

## Step 4: Introducing the Matrix Generator

To generate matrices, we'll use an object called `MatrixGenerator`. This object will listen to agents' requests to craft matrices and respond accordingly.


```python
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.events.abstracts.action import AbstractAction

# Create two events and one action
# Event that the agent will use to generate a matrix
class AgentGeneratesNxNMatrixEvent(AbstractEvent):
    event_type = "agent_generates_n_by_n_matrix_event"
    description = "An agent generates a squared matrix of size N of integer numbers. The target_id of this event is the matrix generator object."
    N: int

# Event that the MatrixGenerator Object will use to give the requested matrix to the agent
class SendGeneratedMatrixEvent(AbstractEvent):
    event_type = "send_generated_matrix_event"
    description = "Sends the requested squared matrix of size N of integer numbers to the agent"
    matrix: List[List[int]]
        
class GenerateSquaredMatrix(AbstractAction):
    trigger_event_class = AgentGeneratesNxNMatrixEvent
    description = "Generates squared matrices of size N."
    
    def __init__(self, host_object: AbstractObject):
        self.host_object = host_object
    
    def __call__(self, event:AgentGeneratesNxNMatrixEvent):
        import numpy as np
        N = event.N
        matrix = np.random.randint(100, size=(N, N))
        event = SendGeneratedMatrixEvent(
            sender_id=self.host_object.id,
            target_id=event.sender_id,
            matrix = matrix.tolist(),
        
        )
        self.host_object.send_event(event)

# Define the MatrixGenerator Object
class MatrixGenerator(AbstractObject):
    def __init__(self, id:str):
        actions = [GenerateSquaredMatrix(host_object=self)]
        super().__init__(name="Matrix Generator", 
                         id=id, 
                         description="Object used to random integer squared matrices.", 
                         actions=actions
                         )

# Instantiate the MatrixGenerator Object
matrix_generator = MatrixGenerator(id="matrix_generator")

# Incorporate the Matrix Generator into the Simulation
CMD_world.add_object(matrix_generator)
```

```output
    INFO:     ('127.0.0.1', 56962) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [33m[matrix_generator Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:matrix_generator Thread:Connected to world socket server ws://127.0.0.1:7456/ws
```    

## Testing without Agents

This is the easiest way to test the new actions or events that you build into objects. Because testing directly without the agent is faster, and you don't depend on the non-deterministic choice of the next action, which can potentially fail.


```python
from genworlds.utils.test_user import TestUser

# Create a Testing User
test_user = TestUser()
```

```output
    INFO:     ('127.0.0.1', 56963) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [34m[test_user Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:test_user Thread:Connected to world socket server ws://127.0.0.1:7456/ws
```    


```python
message_to_send = AgentGeneratesNxNMatrixEvent(
    sender_id=test_user.id,
    target_id="matrix_generator",
    N=10
).json()

test_user.socket_client.send_message(message_to_send)
```

```output
    {"event_type": "agent_generates_n_by_n_matrix_event", "description": "An agent generates a squared matrix of size N of integer numbers. The target_id of this event is the matrix generator object.", "summary": null, "created_at": "2023-10-09T11:51:52.606195", "sender_id": "test_user", "target_id": "matrix_generator", "N": 10}
    {"event_type": "send_generated_matrix_event", "description": "Sends the requested squared matrix of size N of integer numbers to the agent", "summary": null, "created_at": "2023-10-09T11:51:52.608195", "sender_id": "matrix_generator", "target_id": "test_user", "matrix": [[43, 43, 56, 34, 65, 35, 84, 93, 46, 56], [11, 13, 54, 31, 22, 15, 54, 45, 86, 6], [3, 62, 35, 62, 31, 41, 70, 68, 79, 37], [69, 49, 80, 38, 37, 76, 97, 39, 13, 28], [49, 33, 58, 81, 16, 79, 96, 56, 48, 17], [20, 6, 79, 90, 67, 86, 32, 75, 72, 2], [92, 78, 30, 1, 83, 65, 52, 1, 43, 82], [66, 30, 60, 79, 79, 50, 47, 54, 72, 42], [27, 38, 60, 58, 89, 55, 23, 37, 66, 34], [96, 32, 28, 69, 83, 61, 22, 52, 71, 57]]}
```

## Step 5: Basic Assistant
Now we are going to instantiate and attach `John` to the World, which is a `BasicAssistant`. That means that it does not have any specific thought a part from those included in the `think_n_do` loop which is mainly selecting the next action to execute, and fill its triggering event.

When it has nothing to do then waits for a `wakeup_event` to start back again.


```python
from genworlds.agents.concrete.basic_assistant.utils import generate_basic_assistant
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent
from genworlds.agents.concrete.basic_assistant.actions import AgentSpeaksWithAgentEvent


agent_name = "John"
description = """Agent that helps the user generate random matrices. Can talk to other agents to ask for information."""

# Generate a Dummy Agent named John
john = generate_basic_assistant(
    agent_name=agent_name, 
    description=description,
    openai_api_key=openai_api_key
)

john.add_wakeup_event(event_class=UserSpeaksWithAgentEvent)
john.add_wakeup_event(event_class=AgentSpeaksWithAgentEvent)

## Attach John to the Simulation
CMD_world.add_agent(john)
```

```output
    INFO:     ('127.0.0.1', 56964) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [36m[John Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:John Thread:Connected to world socket server ws://127.0.0.1:7456/ws
    

    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T11:51:55.516320", "sender_id": "John", "target_id": "72581673-a808-462f-b903-39d1ae4c9d2f"}
    ...
    You can find full outputs on GitHub.
    ...
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T11:52:05.117570", "sender_id": "John", "target_id": null}
    Agent goes to sleep...
```    

## Step 6: Simulating User Interaction with the Agent

In this step, we'll demonstrate how to simulate user interaction with the agent in the simulation environment. The objective is to have a pseudo-user send a request to our dummy agent "John", asking him to perform specific tasks. This helps in understanding the dynamics of agent-user communication and to observe how the agent reacts and processes user's requests.


```python
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent

# Format the message that will be sent to the simulation socket
test_msg = "Hey John, generate a 4x4 matrix and send it to me please!"
message_to_send = UserSpeaksWithAgentEvent(
    sender_id=test_user.id,
    message=test_msg, 
    target_id="John"
).json()

# Send the message to John
test_user.socket_client.send_message(message_to_send)
```

```output
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T11:53:01.816272", "sender_id": "test_user", "target_id": "John", "message": "Hey John, generate a 4x4 matrix and send it to me please!"}
    Agent is waking up...
    ...
    You can find full outputs on GitHub.
    ...
    Agent goes to sleep...
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T11:53:54.047908", "sender_id": "John", "target_id": null}
```

## Step 7: Integrating a Determinant Calculator into the Simulation

In this step, we will introduce an object into our simulation environment that agents can utilize to compute the determinant of matrices. This serves as a representation of how tools and utilities can be made available to agents, enhancing their capabilities.


```python
from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.events.abstracts.action import AbstractAction

# Event that the agent will use to compute the determinant of a given matrix
class AgentComputesDeterminant(AbstractEvent):
    event_type = "agent_computes_determinant"
    description = "An agent computes the determinant of a matrix"
    matrix: List[List[int]]

# Event that the DetCalculator Object will use to give the requested determinant to the agent
class SendMatrixDeterminant(AbstractEvent):
    event_type = "send_matrix_determinant"
    description = "Sends the requested determinant of the matrix to the agent"
    determinant: int
        
class ComputeDeterminant(AbstractAction):
    trigger_event_class = AgentGeneratesNxNMatrixEvent
    description = "Generates squared matrices of size N."
    
    def __init__(self, host_object: AbstractObject):
        self.host_object = host_object
    
    def __call__(self, event: AgentComputesDeterminant):
        import numpy as np
        determinant = np.linalg.det(np.array(event.matrix))
        event = SendMatrixDeterminant(
            sender_id=self.host_object.id,
            target_id=event.sender_id,
            determinant = determinant,
        )
        self.host_object.send_event(event)

# Define the DetCalculator Object
class DetCalculator(AbstractObject):
    def __init__(self, id:str):
        actions = [ComputeDeterminant(host_object=self)]
        super().__init__(name="Determinant Calculator", 
                         id=id, 
                         description="Object used to compute determinants of squared matrices.", 
                         actions=actions
                         )

# Instantiate the DetCalculator Object
det_calculator = DetCalculator(id="det_calculator")

# Incorporate the Determinant Calculator into the World
CMD_world.add_object(det_calculator)
```

```output
    INFO:     ('127.0.0.1', 56968) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [37m[det_calculator Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:det_calculator Thread:Connected to world socket server ws://127.0.0.1:7456/ws
```    

## Step 8: Introducing Another Agent and Requesting World State Updates
In this step, we will be adding a second agent, "Matthew", to our simulation. Both John and Matthew will then request updates on the world state, allowing them to become aware of each other and other changes in the simulation environment.


```python
from genworlds.agents.concrete.basic_assistant.utils import generate_basic_assistant
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent
from genworlds.agents.concrete.basic_assistant.actions import AgentSpeaksWithAgentEvent

agent_name = "Matthew"
description = """Agent that helps to compute determinants of matrices. Can talk to other agents to ask for information."""

# Generate a Dummy Agent named John
matthew = generate_basic_assistant(
    agent_name=agent_name, 
    description=description,
    openai_api_key=openai_api_key
)

matthew.add_wakeup_event(event_class=UserSpeaksWithAgentEvent)
matthew.add_wakeup_event(event_class=AgentSpeaksWithAgentEvent)


## Attach DCPI to the Simulation
CMD_world.add_agent(matthew)
```

```output
    INFO:     ('127.0.0.1', 56969) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [31m[Matthew Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:Matthew Thread:Connected to world socket server ws://127.0.0.1:7456/ws
    

    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T11:54:28.079080", "sender_id": "Matthew", "target_id": "72581673-a808-462f-b903-39d1ae4c9d2f"}
    ...
    You can find full outputs on GitHub.
    ...

    Agent goes to sleep...
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T11:54:36.110221", "sender_id": "Matthew", "target_id": null}
```    

## Step 9: Final Collaborative Test between Agents

In the final step of this tutorial, we're putting everything together to demonstrate how agents can collaborate in the simulation world. We'll instruct John to generate a 3x3 matrix, have its determinant computed by Matthew, and then relay the matrix and its determinant back to us, the user.


```python
test_msg = """Hey John, 
generate a matrix 3x3, 
send it to Matthew (which is an agent) to compute its determinant, 
and when he replies back to you, tell me the matrix and its determinant. 
While you wait for Matthew to send you the response, you can go to sleep."""

message_to_send = UserSpeaksWithAgentEvent(
    sender_id=test_user.id,
    message=test_msg, 
    target_id="John"
).json()

# Send the message to John
test_user.socket_client.send_message(message_to_send)
```

```output
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T11:56:36.030812", "sender_id": "test_user", "target_id": "John", "message": "Hey John, \ngenerate a matrix 3x3, \nsend it to Matthew (which is an agent) to compute its determinant, \nand when he replies back to you, tell me the matrix and its determinant. \nWhile you wait for Matthew to send you the response, you can go to sleep."}
    Agent is waking up...
    ...
    You can find full outputs on GitHub.
    ...
```    

## Conclusions

Congratulations on reaching the end of this tutorial on simulating agent collaboration in the GenWorlds environment! 

Let's reflect on what we've accomplished and what we've learned:

### Key Takeaways:
1. **Basics of the GenWorlds Framework:**
    - We began with a solid foundation, introducing the core components and functionalities of the GenWorlds simulation framework. This framework is powerful and flexible, enabling the creation and management of complex agent-driven worlds.
2. **Creation of Dummy Agents:**
    - We went through the process of creating basic, dummy agents and setting up their attributes. This gave us a hands-on understanding of agent attributes like name, role, background, and their thought processes like navigation_brain.
3. **User-Agent Interaction:**
    - We designed a Fake User to simulate real-world interactions between users and agents in the environment. This user-agent interaction plays a crucial role in instructing agents and receiving feedback from them.
4. **Defining Custom Events & Objects:**
    - Our tutorial introduced the concept of custom events, allowing us to define specific actions like matrix determinant computation. We also learned about objects in the simulation, such as our "Determinant Calculator."
5. **Inter-Agent Collaboration:**
    - One of the highlights was demonstrating how agents can collaborate. We instructed John to create a matrix, which was then processed by Matthew, showcasing the potential for multi-agent workflows.

### Further Exploration:
While we've covered a lot, the GenWorlds environment offers even more to explore:
- **Complex Agent Behaviors:** Our tutorial focused on basic, dummy agents. Delve deeper into the framework to create agents with intricate behaviors, decision-making processes, and reactions to diverse events.
- **Expand the World:** Introduce more objects, locations, and complexities to your simulation. Imagine scenarios like agents navigating through a maze or collaborating to solve puzzles.
- **Real-time Analytics:** With multiple agents and complex events, the simulation can produce vast amounts of data. Dive into analyzing this data to gain insights into agent behaviors, interactions, and more.

### Wrapping Up:
Agent-based simulations like GenWorlds are powerful tools for modeling complex systems and interactions. They offer insights into multi-agent behaviors, decision-making processes, and collaborative efforts. By mastering these simulations, you'll be equipped to tackle intricate problems, design intelligent systems, and model real-world scenarios with confidence.

Thank you for journeying through this tutorial with us. We hope it has sparked your interest in exploring the vast possibilities of agent-based simulations further!
