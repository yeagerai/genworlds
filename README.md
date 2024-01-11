# 🧬🌍 GenWorlds

GenWorlds is a minimalist framework for building event-based simulations where autonomous AI agents operate. Maintained by [@yeagerai](https://twitter.com/yeagerai)

<h3>

[Homepage](https://genworlds.com/) | [Documentation](https://genworlds.com/docs) | [Examples](https://genworlds.com/examples)

</h3>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/license/mit/) [![Discord](https://dcbadge.vercel.app/api/server/VpfmXEMN66?compact=true&style=flat)](https://discord.gg/VpfmXEMN66) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/yeagerai.svg?style=social&label=Follow%20%40YeagerAI)](https://twitter.com/yeagerai) [![GitHub star chart](https://img.shields.io/github/stars/yeagerai/genworlds?style=social)](https://star-history.com/#yeagerai/genworlds)

Is designed for developers and researchers looking to explore and experiment with AI-driven autonomous agents in simulated environments. At its core, it offers a simple yet powerful platform for building and running scalable simulations, with a focus on asynchronous event handling. GenWorlds provides the essential tools to create complex, intelligent agent behaviors in customizable worlds, ensuring both ease of use and advanced functionality.

## Installation 
```
pip install genworlds
```

## Features
- **Dynamic Simulations:** Create virtual worlds that host both entities and agents. These components interact with each other through actions that process and trigger events.
- **Asynchronous Event Handling:** Utilizes async Queues for efficient management of simultaneous events and actions, ensuring responsive and scalable simulations.
- **Decorator-Based Action Design:** Simplifies the creation and management of actions for agents and entities, enhancing ease of use and flexibility.
- **Support for Various LLMs:** Compatible with a wide range of open-source Large Language Models (LLMs), integration with Ollama, and various GPT models from OpenAI.
- **Customizable States:** Offers the ability to tailor the states of agents and entities to meet specific requirements of different simulations.
- **WebSocket Integration:** Facilitates real-time interaction with external services, allowing for dynamic and responsive updates within the simulation environment.
- **Chat Utility Layer:** We provide already built agents and worlds to interact with them through a chat interface ala ChatGPT. You can find the interface [here](https://github.com/yeagerai/genworlds-community).


## Warnings

- **GenWorlds is still alpha software so is under active development**
- **When not using Open Source LLMs, using GenWorlds can be costly due to API calls**


## Contributing

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation. Please read our [CONTRIBUTING](https://github.com/yeagerai/genworlds/blob/main/CONTRIBUTING.md) for guidelines on how to submit your contributions.

As the framework is in alpha, expect large changes to the codebase.
