---
sidebar_position: 6
---

# Marketplace - Coming Soon

The Genworlds Marketplace will enable anyone to list and sell Worlds and Agents.

## For Agent developers

Monetize your hard-earned prompt-engineering skills and let your agents work for others while you sleep - all the while the Genworlds platform will handle hosting for your.

## For Users

Build your team with the best agents in the world. Rent entire Worlds set up for specific tasks, or create your own with GenWorlds Hosted Agents.

```mermaid
flowchart TD
    subgraph Simulation
        W1(Simulation Socket)
        W2(Simulation API Gateway)
        subgraph World
            A1(Agent 2)
            A2(Agent 3)
            AN(... Agent N)
            O1(Object 1)
            O2(Object 2)
            ON(... Object M)
        end
    W1<-->A1
    W1<-->W2
    W1<-->A2
    W1<-->AN
    W1<-->O1
    W1<-->O2
    W1<-->ON
    end
    I1(User with Simulation API Key)
    G(GenWorlds GATEWAY)
    W2<-->I1
    G<-->Simulation
    style W2 stroke:#f66,stroke-dasharray: 5 5,stroke-width:3px
    style G stroke:#f66,stroke-dasharray: 5 5,stroke-width:3px
```
