---
sidebar_position: 1
---

# Agents

Agents are the entities that are both active and reactive within the world. They have a set of goals and try to accomplish them by planning a series of actions. Also they can trigger non-determinstic actions named `ThoughtActions`.

More specifically, agents are entities that inherit from `AbstractAgent`, our interface class that gives them the boundaries and conditions that they must follow.

In particular, GenWorlds agents always work using the following mental model:

```python
def think_n_do(self):
    """Continuously plans and executes actions based on the agent's state."""
    while True:
        try:
            sleep(1)
            if self.state_manager.state.is_asleep:
                continue
            else:
                state = self.state_manager.get_updated_state()
                action_schema, trigger_event = self.action_planner.plan_next_action(
                    state
                )

                if action_schema.startswith(self.id):
                    selected_action = [
                        action
                        for action in self.actions
                        if action.action_schema[0] == action_schema
                    ][0]
                    selected_action(trigger_event)
                else:
                    self.send_event(trigger_event)
        except Exception as e:
            print(f"Error in think_n_do: {e}")
            traceback.print_exc()
```

And agents run two parallel threads, one that is the event listener and the other one that executes the `think_n_do` function.

Here is the breakdown of this specific mental model at each step of their interaction with the world:

1. **Reviewing the world state and surrounding entities:** The agent assesses the environment it's and gets the available entities and actions.

2. **Selects next action to perform:** Based on its memories of what happened during the simulation and the available actions that it can choose to do, it selects which is going to be the next action that will help him get closer to its goals.

3. **Fills the triggering event:** Using its stored memories, the agent recalls past experiences outputs from other pre-defined `ThoughtActions`, it fills the next event that it will send to the socket.

4. **Executes the action or sends the event:** If the triggering event that it filled is the trigger of an agent's action, then it executes the action. And if that's not the case, then it sends the event to the socket. So the other entity will receive it and will be able to react to it.

This interactive process fosters the emergence of complex, autonomous behavior, making each agent an active participant in the GenWorld.

## Agent State

The agent's state is where all the information about the agent is stored. It's a `pydantic.BaseModel` that has the following fields:

* `id`: Unique identifier of the agent.
* `description`: Description of the agent.
* `name`: Name of the agent.
* `host_world_prompt`: Prompt of the host world.
* `memory_ignored_event_types`: Set of event types that will be ignored and not added to memory of the agent.
* `wakeup_event_types`: Events that can wake up the agent.
* `action_schema_chains`: List of action schema chains that inhibit the action selector.
* `goals`: List of goals of the agent.
* `plan`: List of actions that form the plan.
* `last_retrieved_memory`: Last retrieved memory of the agent.
* `other_thoughts_filled_parameters`: Parameters filled by other thoughts.
* `available_action_schemas`: Available action schemas with their descriptions.
* `available_entities`: List of available entities in the environment.
* `is_asleep`: Indicates whether the agent is asleep.
* `current_action_chain`: List of action schemas that are currently being executed.

Those fields are accessed during the `think_n_do` process to make decisions about the next action to perform.

## BasicAssistant

The `BasicAssistant` is the simplest useful agent that you can create. It's a subclass of `AbstractAgent` that has a set of pre-defined actions that are useful for most agentic environments. Is the central part of the framework's basic utility layer.

Also it can be easily extended to create more complex agents that inherit from it. In our experience, custom agents that inherit from `BasicAssistant` can cover most of the use cases that we have encountered.

You can find more information about how to use agents and create custom agents in the tutorials section of this documentation.
