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

The current version of GenWorlds is powered by [OpenAI's GPT4](https://openai.com/product/gpt-4), [Langchain](https://python.langchain.com/en/latest/index.html), [qdrant](https://cloud.qdrant.io?ref=yeagerai), and was inspired by [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT).

## 🚀 Key Features

- 🌐 **Customizable Interactive Environments:** Design unique GenWorld environments, tailored to your project's needs, filled with interactive objects and potential actions for your agents.

- 🎯 **Goal-Oriented Generative Autonomous Agents:** Utilize AI agents powered by Langchain that are driven by specific objectives and can be easily extended and programmed to simulate complex behaviors and solve intricate problems.

- 🧩 **Shared Objects:** Populate your world with shared objects, creating opportunities for your agents to interact with their environment and achieve their goals.

- 💡 **Dynamic Memory Management:** Equip your agents with the ability to store, recall, and learn from past experiences, enhancing their decision-making and interaction capabilities.

- ⚡ **Scalability:** Benefit from threading and WebSocket communication for real-time interaction between agents, ensuring the platform can easily scale up as your needs grow.

# Running on Replit

The easiest way to get started with the Genworlds framework is on Replit.

Simply go to the [Replit Genworlds-Community Fork](https://replit.com/@yeagerai/genworlds-community) and click RUN.

After that, you can fork the project and start playing around with the world setup in the [use_cases/rountable/world-definition.yaml] file to try out your ideas.

# Running locally
## Requirements

Currently the framework needs to be run in a [Conda](https://docs.conda.io/en/latest/) environment, because some of the dependencies can only be installed with conda.
## Installation
### Conda
Before installing the package with pip, you need to set up your conda environment.

First, set up a new conda environment:

```bash
conda create -n genworlds python=3.11
conda activate genworlds
```

Then, install the following dependencies:

#### On Windows

You also need to install [Faiss](https://github.com/facebookresearch/faiss)

```bash
conda install -c conda-forge faiss-cpu
```

#### On Mac OS

```bash
conda install scipy
conda install scikit-learn
conda install -c pytorch faiss-cpu
```

### Pip

After that, you can use pip to install the package:

```bash
pip install genworlds
```

## Run the Rountable example

Start the websocket server and the CLI:

```bash
genworlds-socket-server
genworlds-cli

```

Then in another terminal run the example:

```bash
python use_cases/roundtable/world_setup_tot.py
```

See (use_cases/roundtable/world_setup_tot.py) for the code.

## Usage in your own project
Importing the framework:

```bash
import genworlds
```

See examples for more details.

Before running a simulation, you also need to run the websocket server that will be used for communication between the agents and the world. And also the CLI to visualize what the simulated agents are doing.

```bash
genworlds-socket-server
```

The default port is 7456, but you can change it with the `--port` argument.
You can also set the host with the `--host` argument.

```bash
genworlds-socket-server --port 1234 --host 0.0.0.0
```

# Documentation

The full documentation can be found at [https://genworlds.netlify.app/]

# Contributing  

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation. Please read our CONTRIBUTING for guidelines on how to submit your contributions.

As the framework is in alpha, expect large changes to the codebase.

## Building locally

Clone the repository

```bash
pip install -r requirements.txt
```

### Running in VS Code

The easiest way to run the world is using the Visual Studio Code run configuration.

This will launch all 3 components of the framework - the socket server, the CLI and the example use case - with a debugger attached.

# License

🧬🌍 GenWorlds is released under the MIT License. Please see the LICENSE file for more information. 

# Disclaimer
This software is provided 'as-is', without any guarantees or warranties. By using GenWorlds, you agree to assume all associated risks, including but not limited to data loss, system issues, or any unforeseen challenges.

The developers and contributors of GenWorlds are not responsible for any damages, losses, or consequences that may arise from its use. You alone are responsible for any decisions and actions taken based on the information or results produced by GenWorlds.

Be mindful that usage of AI models, like GPT-4, can be costly due to their token usage. By using GenWorlds, you acknowledge that you are responsible for managing your own token usage and related costs.

As an autonomous system, GenWorlds may produce content or execute actions that may not align with real-world business practices or legal requirements. You are responsible for ensuring all actions or decisions align with all applicable laws, regulations, and ethical standards.

By using GenWorlds, you agree to indemnify, defend, and hold harmless the developers, contributors, and any associated parties from any claims, damages, losses, liabilities, costs, and expenses (including attorney's fees) that might arise from your use of this software or violation of these terms.
