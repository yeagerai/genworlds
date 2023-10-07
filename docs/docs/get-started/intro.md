---
sidebar_position: 1
---

# Introduction

GenWorlds is the event-based communication framework for building multi-agent systems.

Using a websocket, GenWorlds provides a platform for creating interactive environments where AI agents asynchronously interact with each other and their environments to collectively execute complex tasks.

## Main value props

1. **Make What You Want: Customizable Systems**
    - **Abstraction Layer:** Interface with basic primitives, allowing you to build agents, objects, and worlds without predefined limits.
    - **Deterministic & Non-Deterministic Processes:** Manage the reliability and accuracy of your system by controlling process types.

2. **Build Fast: Pre-Built Elements**
    - **Utility Layer:** Comes with ready-made agents, objects, and worlds, enabling quick setup while still permitting customization to cater to most use cases.

3. **Deploy Easily: Designed for Smooth Launches**
    - **Web-Socket Server at Core:** Each GenWorld is a FastAPI web-socket server, thus it can be dockerized and deployed without hassle.
    - **Versatile Connectivity:** The web-socket nature also means you can straightforwardly connect to frontends, backends, or your servers, much like any other web-socket server, offering broad interoperability with most web systems.

## Get Started

Here is how to install GenWorlds, and get started with your first multi-agent system. We highly recommend to follow the [Quickstart guide](/docs/get-started/quickstart.md), but if your prefer, you can jump directly to the tutorials.

## Core Framework Primitives

Before you dive into the specifics, it's crucial to understand the primitives that underpin GenWorlds:

- [**Worlds:**](/docs/genworlds-framework/worlds.md) is the stage of action, tracking agents, objects, and world-specific attributes. It provides agents with real-time updates on the world state, available entities, actions, and events, facilitating interactions.

- [**Objects:**](/docs/genworlds-framework/objects.md) are the essential interactive elements, each defined by unique action sets. We tend to use objects when we want to trigger deterministic processes.

- [**Agents:**](/docs/genworlds-framework/agents/agents.md) Autonomous goal-driven entities, strategizing actions to interact with the world. They learn dynamically about the environment, utilizing objects around them to meet their objectives.

- [**Actions:**](/docs/genworlds-framework/actions.md) Routines that are triggered by an event, and usually the end up sending another event to the socket. Is the main way to define worlds, objects, and agents.

- [**Events:**](/docs/genworlds-framework/actions.md) Payloads of information that essentially are the state of the world.

- [**Thoughts:**](/docs/genworlds-framework/agents/thought_actions.md) Essentially calls to LLMs that will non deterministically fill parameters of the events that will be sent to the socket.

## Tutorials

The best way to understand the GenWorlds framework is to see it in action. The following tutorials will give you a taste of what you can achieve with GenWorlds.

### Introductory

Again, if you are new to the topic of autonomous AI Agents, we highly recommend to follow the [Quickstart guide](/docs/get-started/quickstart.md).

- [Foundational RAG World](https://genworlds.com/) An example of a RAG (Retrieval Augmented Generation) World that can be used as a foundational piece from where to expand and create a knowledge source of your projects. Here you will learn a lot about deterministic actions and objects.
- [Custom Q&A Agent](https://genworlds.com/) In this tutorial, you will learn how you can create custom autonomous agents that have multiple thoughts and how they get integrated into already existing worlds.

### Collaboration Methods

- [First-Steps](https://genworlds.com/) An example of a basic world, with two agents that cooperate to achieve a very simple task.
- [Token Bearer (Roundtable)](https://genworlds.com/) An example of a multi-agent system, where agents interact with each other speaking through a microphone, which is a token to communicate and to signal to the other Agents whose turn it is to perform an action.
