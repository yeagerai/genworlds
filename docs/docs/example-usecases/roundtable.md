---
sidebar_position: 2
---

# Roundtable

[The Roundtable](https://github.com/yeagerai/genworlds-community/tree/main/use_cases/roundtable) world enables you to create a simulated group discussion in the form of a podcast with anyone, on any topic. The agents can even be pre-loaded with custom memories that have been generated from public content, so that they can remember the past views and actions of the characters they're emulating.

The roundtable use-case is a conversational scenario that involves a group of individuals, typically thought leaders or experts, who discuss a certain topic. In the GenWorlds framework, this use-case is represented by a YAML configuration file, like `business_luminaires.yaml`. The configuration file defines the agents, objects, and world properties that make up the roundtable scenario.

GenWorlds employs unique mechanics to manage conversational flow in the Roundtable use-case. The key to this coordination is the use of the "Microphone" as a token bearer. The token-bearing approach ensures smooth turn-taking among the participants and regulates when and who gets to speak during the discussion.

## What is a Microphone in the Roundtable Use-Case?

In this use-case, a microphone is a virtual object created and configured within the GenWorlds simulation. The microphone serves as a conversational token that determines who has the speaking right at any given time. The agent currently holding the microphone can speak, make a statement, respond to a question, or even make a joke.

Here's an example of how a microphone might be defined in a configuration:

```yaml
objects:
- id: mic1
  class: use_cases.roundtable.objects.microphone.Microphone
  name: Microphone
  description: A podcast microphone that allows the holder of it to speak to the
    audience. The speaker can choose to make a statement, ask a question, respond
    to a question, or make a joke.
  host: steve_jobs
  world_properties:
    held_by: steve_jobs
```

## How does the Microphone Work as a Coordination Mechanism?

The microphone, as a token bearer, becomes a control mechanism to ensure orderly conversation within the roundtable setup.

### Rules Governing the Microphone

- Only the holder of the microphone can speak to the audience: Agents can participate in the conversation only when they hold the microphone. This prevents overlapping dialogue and ensures each agent has an opportunity to voice their opinion or idea.

- Pass the microphone to respond: If an agent asks a question directed at another agent, the microphone should be passed to the receiving agent for them to respond.

- Don't monopolize the microphone: The agent holding the microphone should ensure they don't occupy the speaking time for an extended period. After making their point or asking a question, they should pass the microphone to the next speaker.

- Immediate action is required: An agent can't indefinitely hold the microphone without speaking or passing it on. Once an agent finishes their turn, they need to promptly pass the microphone to another participant.

The constraints defined in the configuration ensure compliance with these rules. These regulations facilitate a seamless and balanced conversation among the agents.

## How to Pass the Microphone?

Passing the microphone to the next speaker involves transferring the "held_by" property of the microphone to the next agent. When an agent completes their statement or asks a question, they change the "held_by" property to the ID of the next speaker. This action signifies the end of their turn and the beginning of the next agent's turn.

The framework's built-in functions facilitate the transfer of objects like the microphone between agents. This mechanism promotes smooth turn-taking, which is fundamental in creating an engaging and interactive roundtable discussion.

## Wrapping Up

The microphone as a token bearer is a key component in coordinating the Roundtable use-case within the GenWorlds framework. It orchestrates the conversation flow and ensures each agent gets their turn to speak, fostering an engaging, organized, and orderly discussion. With such a mechanism, GenWorlds provides a unique and efficient approach to simulate complex roundtable discussions among multiple agents.
