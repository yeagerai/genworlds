---
sidebar_position: 3
---

# Objects

Objects in GenWorlds play a crucial role in facilitating interaction between agents. Every object defines a unique set of events, enabling agents to accomplish specific tasks and work together in a dynamic environment. Objects can be in an agent's vicinity or can be part of their inventory, expanding the scope of possible interactions.

:::tip Info

Objects are the main way to give Agents new capabilities and organize them in a structure to achieve a broader goal.

::: 

Agents are designed to adapt dynamically, learning about nearby objects, understanding the event definitions, and determining the best way to interact with them to achieve their goals.

Objects in GenWorlds are versatile and can be subclassed to achieve varying purposes, such as 'token bearers' or 'tools'. For instance, a 'token bearer' like a microphone in a podcast studio, can be passed among agents, fostering a collaborative environment. The agent currently holding the token (or the microphone) gains the ability to perform unique actions, like speaking to the audience. This mechanism introduces the notion of shared resources and cooperative interactions, reinforcing that objects aren't confined to one agent, but can be easily exchanged and used throughout the collective.

A 'tool', on the other hand, can execute specific functions such as calling external APIs, running complex calculations, or triggering unique events in the world.

:::tip Objects

Objects are the main way to give new abilities to agents, to have them accomplish a specific task, as well as enable them working together.

:::

```python
microphone = Microphone(
    id="microphone",
    name="Microphone",
    description="A podcast microphone that allows the holder of it to speak to the audience",
    host=podcast_host.id
)
```

This way, by defining various objects and mapping them to specific events, you can design rich and complex interactions in the GenWorlds environment. Objects essentially extend the capabilities of agents, making them central to the game's narrative and task accomplishment.
