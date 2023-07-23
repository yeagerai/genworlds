---
sidebar_position: 1
---

# Introduction

[The Roundtable](https://github.com/yeagerai/genworlds-community/tree/main/use_cases/roundtable) world enable you to create a podcast with anyone, on any topic. The agents can even be pre-loaded with custom memories that have been generated from public content, so that they can remember the past views and actions of the characters they're emulating.

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

    I1(Community Toolkit)
    W1<-->A1
    W1<-->A2
    W1<-->AN
    W1<-->O1
    W1<-->O2
    W1<-->ON
    W1<-->I1

    style I1 stroke:#f66,color:#fff,stroke-dasharray: 5 5,stroke-width:3px
```

```mermaid
graph LR
    subgraph Community-Toolkit
        subgraph Frontend
            A[Frontend interface - Vue]
        end
        
        subgraph Backend
            C[World Instance - FastAPI REST]
            F[16bit game backend - TS + Colyseus]
            G[Redis Server]
            D[Real web socket - FastAPI WS]
            E[Mocked web socket - FastAPI WS]
            B[16bit game interface - TS + Phaser.io]
            H[Gateway server - JS]
        end
    end
    
    C <--> D
    B <--> F
    D <--> F
    E <--> C
    F <--> E
    F <--> G

    A <--Calls servers using subpaths http/s--> H
    B <--http--> H
    C <--http--> H
    F <--ws--> H
    D <--ws--> H
    E <--ws--> H
    style Community-Toolkit stroke:#f66,color:#fff,stroke-dasharray: 5 5,stroke-width:3px
```

## How it's built

It works by having a Microphone that each agent can have in their inventory. Only the holder of the microphone can speak, and they need to pass it on to the next speaker. The microphone solves the coordination problem of multiple agents speaking over each other.

It showcases how multiple agents can coordinate and work together using objects and their inventory.
