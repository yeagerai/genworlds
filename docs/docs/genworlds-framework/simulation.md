---
sidebar_position: 1
---

# Simulation

A Simulation is the highest level abstraction in the Genworlds framework. It ties together a [World](/docs/genworlds-framework/world.md), [Agents](/docs/genworlds-framework/agents/agents.md) and [Objects](/docs/genworlds-framework/objects.md), starts and manages their threads.

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

    style Simulation stroke:#f66,color:#fff,stroke-dasharray: 5 5,stroke-width:3px
```

## Creating a Simulation

```python
simulation = Simulation(
    name="Example Simulation",
    description="This is an example simulation",
    world=world,
    objects=objects,
    agents=agents,
)

# this attaches to the websocket all the objects and agents in the world
simulation.launch()
```

## Websocket Server

The [World](/docs/genworlds-framework/world.md), [Agents](/docs/genworlds-framework/agents/agents.md) and [Objects](/docs/genworlds-framework/objects.md) all interact through a websocket server and communicate by sending events. This allows for parallel operation, easily connecting a frontend or some other service to the world, as well as running agents on external servers, such as the Genworlds Marketplace.
