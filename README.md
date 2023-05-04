# The yAgents Research Pod
[WARNING: ULTRA-BETA]

The pod that creates, ensembles, and deploys agents on demand.

By now the `yeager_core` is included in this repo as a python module but will be moved out in the future.

## Setup

`conda install -c conda-forge faiss-cpu`
https://github.com/facebookresearch/faiss/blob/main/INSTALL.md

`pip install -r requirements.txt`

### Set up environment variables

Copy the contents of .env.example to `~/.yeagerai-sessions/.env` and fill in the values

## Usage

Run the server
`uvicorn world_socket_server:app --host 0.0.0.0 --port 7456`

Run the world from VSCode


## TODO List (Features)
**Generative Agents missing features:**
- it should have a master prompt with access to vectorial memories 🔲
- it should execute actions based on the current plan 🔲
- it should have a series of world actions and tools like (ask for feedback, or find character) 🔲
- it should have a success_score where measures the effectivity of the agent while doing the task outlined in the master prompt 🔲
- it should have a separation_email tool that asks for being splitted into two agents to improve performance 🔲


**Research Pod required features:**
- Positions and access to the agents 🔲
- Can add or remove agents in the pod 🔲
- Manages the pseudo-randomness and interactions of the agents 🔲
- Have critical elements such as library, blackboard, etc. 🔲
- Humans can only interact with agents through the pod, modifying the blackboard or adding/removing agents, etc. 🔲
- Implement different output storages, like files and folders to store outputs of the pod. 🔲

**yAgent Research Pod:**
- Missing Agents:
    - yTools: 🟨
    - yMemories: 🟨
    - yMasterPrompts: 🔲
    - yDebug: 🔲
    - yDeploy: 🔲
    - yPolice: 🔲
    - yDirector: 🔲

- The output should be a folder, containing all the files of the newly created agent, and this already deployed into the cloud.