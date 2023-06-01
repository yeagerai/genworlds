# 🧬🌍 GenWorlds - The Collaborative AI Agent Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/license/mit/) 
[![](https://dcbadge.vercel.app/api/server/VpfmXEMN66?compact=true&style=flat)](https://discord.gg/VpfmXEMN66) 
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/yeagerai.svg?style=social&label=Follow%20%40YeagerAI)](https://twitter.com/yeagerai) 
[![GitHub star chart](https://img.shields.io/github/stars/yeagerai/genworlds?style=social)](https://star-history.com/#yeagerai/genworlds)


## ⚠️ Warnings!

- **GenWorlds is under active development**
- **OpenAI API Access Required**
- **Using GenWorlds can be costly**


# About
GenWorlds is an open-source framework for building reliable multi-agent systems. 

Drawing inspiration from the seminal research paper ["Generative Agents: Interactive Simulacra of Human Behavior"](https://arxiv.org/abs/2304.03442) by Stanford and Google researchers, GenWorlds provides a platform for creating flexible, scalable, and interactive environments where AI agents can exist, communicate asynchronously, interact with diverse objects, and form new memories.

Agents can also be pre-loaded with a series of memories that give them personality and helps them become subject-matter experts. This feature allows for nuanced and sophisticated interactions and behaviors. These agents communicate with the world through a WebSocket server, promoting ease of UI construction and future scalability. 

The current version of GenWorlds is powered by [OpenAI's GPT4](https://openai.com/product/gpt-4), [Langchain](https://python.langchain.com/en/latest/index.html), [Chroma](https://www.trychroma.com/), and was inspired by [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT).

## 🚀 Key Features

- 🌐 **Customizable Interactive Environments:** Design unique GenWorld environments, tailored to your project's needs, filled with interactive objects and potential actions for your agents.

- 🎯 **Goal-Oriented Generative Autonomous Agents:** Utilize AI agents powered by Langchain that are driven by specific objectives and can be easily extended and programmed to simulate complex behaviors and solve intricate problems.

- 🧩 **Shared Objects:** Populate your world with shared objects, creating opportunities for your agents to interact with their environment and achieve their goals.

- 💡 **Dynamic Memory Management:** Equip your agents with the ability to store, recall, and learn from past experiences, enhancing their decision-making and interaction capabilities.

- ⚡ **Scalability:** Benefit from threading and WebSocket communication for real-time interaction between agents, ensuring the platform can easily scale up as your needs grow.

# Requirements

Currently it needs to be run in a [Conda](https://docs.conda.io/en/latest/) environment, because some of the dependencies can only be installed with conda.

# Installation
## Conda
Before installing the package with pip, you need to set up your conda environment.

First, set up a new conda environment:

```bash
conda create -n genworlds python=3.10
conda activate genworlds
```

Then, install the following dependencies:

### On Windows

You also need to install [Faiss](https://github.com/facebookresearch/faiss)

```bash
conda install -c conda-forge faiss-cpu
```

### On Mac OS

```bash
conda install scipy
conda install scikit-learn
conda install -c pytorch faiss-cpu
```

## Pip

After that, you can use pip to install the package:

```bash
pip install genworlds
```

# Run the Rountable example

Start the websocket server and the CLI:

```bash
genworlds-start-chat-room
```

Then in another terminal run the example:

```bash
python use_cases/roundtable/world_setup_n_launch.py
```

See (use_cases/roundtable/world_setup_n_launch.py) for the code.

# Usage in your own project
Importing the framework:

```bash
import genworlds
```

See examples for more details.

Before running a simulation, you also need to run the websocket server that will be used for communication between the agents and the world. And also the CLI to visualize what the simulated agents are doing.

```bash
genworlds-start-chat-room
```

The default port is 7456, but you can change it with the `--port` argument.
You can also set the host with the `--host` argument.

```bash
genworlds-start-chat-room --port 1234 --host 0.0.0.0
```

## Set up a simulations

A simulation consists of a world, a set of agents, and a set of objects.

```python
simulation = Simulation(
    name="roundtable",
    description="This is a podcast studio. There is a microphone, and only the holder of the microphone can speak to the audience",
    world=world,
    objects=[
        (microphone, {"held_by": podcast_host.id}),
    ],
    agents=[
        (podcast_host, {"location": "roundtable"}),
        (podcast_guest, {"location": "roundtable"}),
    ],
)
```

Running `simulation.launch()` will start the simulation - start all of the threads for the agents, objects and world.

## World
The 'World' in GenWorlds serves as the setting for all the action. It keeps track of all the agents, objects, and world properties such as agent inventories. 

The World ensures every agent is informed about the world state, entities nearby, and the events that are available to them to interact with the world.

The BaseWorld class has been designed with extensibility in mind, enabling the introduction of new world properties. An example of this is the World2D class in our examples, which introduces a location property, adding a spatial dimension to the world.

```python
world = World2D(
    id="world",
    name="roundtable",
    description="This is a podcast studio, where you record the Roundtable podcast. There is a microphone, and only the holder of the microphone can speak to the audience",
    locations=["roundtable"],
)
```

## Agents

Agents are the entities that interact with the world. They have a set of goals and try to accomplish them by planning a series of actions.

The agents interact with their environment by sending events through a WebSocket server initiated by the world. They dynamically learn about the world and the objects around them, figuring out how to utilize these objects to achieve their goals.

```python
podcast_host = YeagerAutoGPT(
    id="maria",
    ai_name="Maria",
    description="The host of the podcast",
    goals=[(
        "Host an episode of the Roundtable podcast, discussing AI technology. \n",
        "Only the holder of the microphone can speak to the audience, if you don't have the microphone in your inventory, wait to receive it from the previous speaker. \n",
        "Don't repeat yourself, respond to questions and points made by other co-hosts to advance the conversation. \n",
        "Don't hog the microphone for a long time, make sure to give it to other participants. \n",
    )],
    openai_api_key=openai_api_key,
    interesting_events={"agent_speaks_into_microphone", "agent_gives_object_to_agent_event"},
)
```

`interesting_events` are the events that will be fed to the agent's prompt, allowing them to pay attention to things that are happening in the world.

### Custom memories 

Each agent can be pre-loaded with unique memories, enhancing its unique personality traits and subject matter expertise. These memories are injected on their prompts based on their relevance to the agent's current goals, allowing for more focused and reliable interactions.

Setting up these custom memories is straightforward with the [Chroma](https://www.trychroma.com/) vector database. Just pass the following parameters to the agent constructor:

```python
personality_db_path="/path/to/db",
personality_db_collection_name="jimmy-sentences",
```

### Agent Mental Model

The Generative Agents within GenWorlds follow a specific mental model at each step of their interaction with the world:

1. **Reviewing the world state and surrounding entities:** The agent assesses the environment it's in and the entities present around it to understand the context before planning any actions.
   
2. **Reviewing new events:** The agent evaluates any new occurrences. These could be actions taken by other agents or changes in the world state due to object interactions.
   
3. **Remembering past events and relevant information:** Using its stored memories, the agent recalls past experiences and data that might affect its current decision-making process.
   
4. **Updating the plan and deciding actions:** Based on the world state, new events, and past memories, the agent updates its action plan and decides on the next actions. These could involve interacting with the world, other agents, or objects. Importantly, an agent can execute multiple actions in one step, improving overall efficiency.
   
5. **Executing the actions:** Finally, the agent implements its plan, influencing the world state and potentially triggering responses from other agents.
   
This interactive process fosters the emergence of complex, autonomous behavior, making each agent an active participant in the GenWorld.

While we are currently focused on enhancing each of these steps, we foresee potential developments in the short-medium term. For instance, we're exploring the value and nature of "reflection" as an aspect of an agent's mental model. This would enable the agent to draw new conclusions from a set of recent memories and maintain high-level goals. We're also considering improvements to the communication systems between agents to facilitate more effective collaboration.

## Objects

Objects are the entities that agents interact with. Each object defines a set of events that the agents can use to interact with them to accomplish their goals.

Agents dynamically learn about nearby objects, and figure out how to use them based on the events that these objects define. Furthermore, objects can be held in an agent's inventory, providing an added layer of interaction.

```python
microphone = Microphone(
    id="microphone",
    name="Microphone",
    description="A podcast microphone that allows the holder of it to speak to the audience",
    host=podcast_host.id
)
```

# Contributing  

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation. Please read our CONTRIBUTING for guidelines on how to submit your contributions.

As the framework is in alpha, expect large changes to the codebase.

## Building locally

`pip install -r requirements.txt`

# Running locally for development

Running the socket server server

```bash
cd genworlds/sockets/
uvicorn world_socket_server:app --host 0.0.0.0 --port 7456
```

The easiest way to run the world is using the Visual Studio Code run configuration.

# License

🧬🌍 GenWorlds is released under the MIT License. Please see the LICENSE file for more information. 

# Disclaimer
This software is provided 'as-is', without any guarantees or warranties. By using GenWorlds, you agree to assume all associated risks, including but not limited to data loss, system issues, or any unforeseen challenges.

The developers and contributors of GenWorlds are not responsible for any damages, losses, or consequences that may arise from its use. You alone are responsible for any decisions and actions taken based on the information or results produced by GenWorlds.

Be mindful that usage of AI models, like GPT-4, can be costly due to their token usage. By using GenWorlds, you acknowledge that you are responsible for managing your own token usage and related costs.

As an autonomous system, GenWorlds may produce content or execute actions that may not align with real-world business practices or legal requirements. You are responsible for ensuring all actions or decisions align with all applicable laws, regulations, and ethical standards.

By using GenWorlds, you agree to indemnify, defend, and hold harmless the developers, contributors, and any associated parties from any claims, damages, losses, liabilities, costs, and expenses (including attorney's fees) that might arise from your use of this software or violation of these terms.
