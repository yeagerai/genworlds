---
sidebar_position: 1
---

# Introduction

GenWorlds is an open source framework that enables you to model rich, autonomous agents that interact with each other and their environment in complex ways. The decision-making logic and behaviors of these agents enable you to create simulated worlds with intricate behaviors.

Agents interact with the world and with objects in the world, and these interactions are encapsulated as events. These events are communicated through sockets, enabling a real-time interaction between agents and the environment.

In this documentation, we will delve into each of these key components, how they interrelate, and provide examples to guide you in understanding and harnessing the power of GenWorlds for your projects.

## Main value props

- **Coordinative Multi-Agent System:** GenWorlds facilitates the creation of intelligent, interactive systems where multiple agents, equipped with specialized brains, can collaborate and lead to complex behaviors.

- **Customizable and Reliable Simulated Environments:** GenWorlds provides the tools to build highly personalized simulated worlds, with unique objects and states, to effectively simulate various scenarios or study new AI dynamics.

## Key Concepts and Terminology

Before you dive into the specifics, it's crucial to understand the primitives that underpin GenWorlds:

- [**Simulation:**](../genworlds-framework/simulation.md) The environment in which agents and objects exist. The world has its own state, which agents can perceive and influence.

- [**World:**](../genworlds-framework/world.md) Ensures every agent is informed about the world state, entities nearby, and the events that are available to them to interact with the world.

- [**Objects:**](../genworlds-framework/objects.md) Items that exist within the world. Agents can interact with objects in various ways, depending on the scenario at hand.

- [**Agents:**](../genworlds-framework/agents.md) Autonomous entities with distinct attributes, behaviors, and goals. They can perceive their environment, make decisions, and execute actions based on their own internal logic.

## Examples

The best way to understand the GenWorlds framework is to see it in action. The following examples will give you a taste of what you can achieve with GenWorlds.

- [RoundTable](https://replit.com/@yeagerai/GenWorlds?v=1) An example of a multi-agent system, where agents interact with each other speaking through a microphone, a token to communicate and to signal to the other Agents whose turn it is to perform an action.
