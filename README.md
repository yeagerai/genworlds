# 🧬🌍 GenWorlds
[WARNING: ULTRA-BETA]

## About

GenWorlds is a framework for building reliable multi-agent systems. 

Agents can inhabit different kinds of worlds, interact with each other asynchronously, use different kinds of objects and form memories.

Agents can also be pre-loaded with a series of memories, to give them personality and help them become subject-matter experts.

The agents interact with the world through a websocket server, making it easy to build various UIs for them, and enabling scalability in the future.

We use [langchain](https://python.langchain.com/en/latest/index.html) and [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT) under the hood.

## Installation

`pip install genworlds`

## Usage
Importing the framework:

```
import genworlds

```

See examples for more details.

### Set up a simulations

A simulation consists of a world, a set of agents, and a set of objects.

```
simulation = Simulation(
    name="roundable",
    description="This is a podcast studio. There is a microphone, and only the holder of the microphone can speak to the audience",
    world=world,
    objects=[
        (microphone, {"held_by": podcast_host.id}),
    ],
    agents=[
        (podcast_host, {"location": "roundtable"}),
        (podcast_guest, {"location": "roundtable"}),
    ],
)
```

Running `simulation.launch()` will start the simulation - start all of the threads for the agents, objects and world.

### World

The world keeps track of all the agents and objects, and world properties such as agent inventories.

The world updates all of the agents about their world state, nearby entities and events they can use to interact with the world.

The BaseWorld class can be extended to introduce new world properties, for example the Wolrd2D in the examples introduces a location property.

```
world = World2D(
    id="world",
    name="roundtable",
    description="This is a podcast studio, where you record the Roundtable podcast. There is a microphone, and only the holder of the microphone can speak to the audience",
    locations=["roundtable"],
)
```

### Agents

Agents are the entities that interact with the world. They have a set of goals and try to accomplish them by planning a series of actions.

They interact with the world through a websocket server, which is started by the world, by sending events.

Agents dynamically learn about the world and objects around them, and figure out how they can use them to accomplish their goals.

```
podcast_host = YeagerAutoGPT(
    id="maria",
    ai_name="Maria",
    description="The host of the podcast",
    goals=[(
        "Host an episode of the Roundtable podcast, discussing AI technology. \n",
        "Only the holder of the microphone can speak to the audience, if you don't have the microphone in your inventory, wait to receive it from the previous speaker. \n",
        "Don't repeat yourself, respond to questions and points made by other co-hosts to advance the conversation. \n",
        "Don't hog the microphone for a long time, make sure to give it to other participants. \n",
    )],
    openai_api_key=openai_api_key,
    interesting_events={"agent_speaks_into_microphone", "agent_gives_object_to_agent_event"},
)
```

`interesting_events` are the events that will be fed to the agent's prompt, allowing them to pay attention to things that are happening in the world.

#### Custom memories 

Agents can be pre-loaded with prepared memories that will be loaded in their prompt based on the relevance to their current goals. These can be used to give agents personality and make them subject-matter experts.

The custom memories are a Chroma vector database, and you can set it up by passing the following two parameters to the agent constructor:
    
    ```
    personality_db_path="/path/to/db",
    personality_db_collection_name="jimmy-sentences",
    ```

### Objects

Objects are the entities that agents can interact with. They define a set of events that the agents can use to interact with them to accomplish their goals.

The agents dynamically learn about nearby objects, and figure out how to use them based on the events they define.

Objects can also be held in inventory by the agents.

```
microphone = Microphone(
    id="microphone",
    name="Microphone",
    description="A podcast microphone that allows the holder of it to speak to the audience",
    host=podcast_host.id
)
```

## Development

Run the server
`uvicorn world_socket_server:app --host 0.0.0.0 --port 7456`

Run the world from VSCode

## Building locally

`conda install -c conda-forge faiss-cpu`
https://github.com/facebookresearch/faiss/blob/main/INSTALL.md

`pip install -r requirements.txt`


## Contributing

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

As the framework is in alpha, expect large changes to the codebase.

## License

MIT
