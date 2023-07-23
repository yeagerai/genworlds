---
sidebar_position: 2
---

# Brains

Brains are the smallest component of the Tree [Agent] (./agent.)

A brain takes as input all the variables of the agent - its name and background, personality, goals, memories and nearby agents and objects - and produces a desired output, through one or more steps.

Brains can be as simple or complex as needed, and allow taking advantage of the latest techniques such as Self-evaluation, Chain-of-Thought, Tree-of-Thought, Committee-of-Experts and any other ones that will be discovered.

Brains take full advantage of [OpenAI Functions](https://openai.com/blog/function-calling-and-other-api-updates) to allow easy specification of the desired output json format.

## Types of Brains

### Zero-Shot brain

This is the simplest type of brain - it produces an output in a single LLM call.

### Single-Eval Brain

This brain uses two LLM calls - the first one to produce multiple possible versions of the desired output, and the second one to pick the best one.

### Multi-Eval Brain

Similar to Single-Eval Brains, a Multi-Eval brain produces a number of possible output options, however instead of a single evaluation call to pick the best output, it calls the evaluation LLM once for each output and asks it to rate it from 1 to 10.

It then sorts then by the rating and picks the best one. It also allows setting a threshold rating - if the best options is below that, the brain instead returns `None`.
