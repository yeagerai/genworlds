---
sidebar_position: 1
---

# Introduction

Welcome to GenWorlds Community Edition, a comprehensive toolkit that empowers you to construct and fine-tune unique AI worlds. Comprising an array of both backend and frontend services, GenWorlds Community Edition harnesses the power of Vue, JavaScript, Redis, WebSockets, and more, providing a well-rounded and potent suite for AI world development.

Whether you prefer using Replit or Docker, GenWorlds Community Edition is readily launchable, ensuring you can operate from your environment of choice.

## Key Features

### Backend and Frontend Services

Empower your AI world with an array of cutting-edge technologies, including Vue for frontend development, JavaScript for a dynamic user experience, Redis for cache management and data storage, and WebSockets for real-time communication. You can find more about the architecture in this document.

### Run Anywhere

With GenWorlds Community Edition, you can launch your AI world seamlessly on Replit or Docker, offering you the flexibility to operate in the environment you are most comfortable with.

### Fine-tune Your World

GenWorlds Community Edition also provides an array of tools allowing you to tailor your AI world according to your unique requirements.

## Architecture Overview

To help you understand the system better, here's an overview of the Simulation and Community Toolkit architectures.

### Simulation

The Simulation comprises a Simulation Socket connected to various Agents and Objects in the World, and it interfaces with the Community Toolkit.

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

    style I1 stroke:#f66,stroke-dasharray: 5 5,stroke-width:3px
```

### Community Toolkit

The Community Toolkit is an integral part of the GenWorlds Community Edition. It consists of a frontend and a backend. The frontend uses Vue, while the backend uses FastAPI, TypeScript, Redis, and more. Here's how they all interconnect:

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
    style Community-Toolkit stroke:#f66,stroke-dasharray: 5 5,stroke-width:3px
```
