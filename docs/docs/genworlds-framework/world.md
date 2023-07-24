---
sidebar_position: 2
---

# World

The 'World' in GenWorlds serves as the setting for all the action. It keeps track of all the agents, objects, and world properties such as agent inventories.

The World ensures every agent is informed about the world state, entities nearby, and the events that are available to them to interact with the world.

```mermaid
graph TD
    subgraph Simulation
        W1(Simulation Socket)
        subgraph World
            A1(Agent 2)
            A2(Agent 3)
            AN(... Agent N)
            O1(Object 1)
            O2(Object 2)
            ON(... Object M)
        end
    end
    I1(Interfaces)
    I2(APIs)
    IN(Backends)
    W1<-->A1
    W1<-->A2
    W1<-->AN
    W1<-->O1
    W1<-->O2
    W1<-->ON
    W1<-->I1
    W1<-->I2
    W1<-->IN

    style World stroke:#f66,stroke-dasharray: 5 5,stroke-width:3px
```

The BaseWorld class has been designed with extensibility in mind, enabling the introduction of new world properties. An example of this is the World2D class in our examples, which introduces a location property, adding a spatial dimension to the world.

```python
world = World2D(
    id="world",
    name="roundtable",
    description="This is a podcast studio, where you record the Roundtable podcast.,
    locations=["roundtable"],
)
```

## World2D

World2D is an extension of the BaseWorld, where each agent and object has a location from a list of locations. Agents only see agents and objects in the same location.

This world also maps to something like a Discord server, where the agent would be in one of many channels at a time.
