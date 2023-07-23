---
sidebar_position: 3
---

# Objects

Objects are the entities that agents interact with. Each object defines a set of events that the agents can use to interact with them to accomplish their goals.

Agents dynamically learn about nearby objects, and figure out how to use them based on the events that these objects define. Furthermore, objects can be held in an agent's inventory, providing an added layer of interaction.

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
