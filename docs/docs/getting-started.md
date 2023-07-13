---
sidebar_position: 2
---

# Getting Started

## Running on Replit

The easiest way to get started with the Genworlds framework is on Replit.

Simply go to the [Replit Genworlds-Community Fork](https://replit.com/@yeagerai/GenWorlds?v=1) and fork it.

After that start playing around with the world setup in the [use_cases/rountable/world-definition.yaml] file to try out your ideas.

## Running locally

### Requirements

Currently the framework needs to be run in a [Conda](https://docs.conda.io/en/latest/) environment, because some of the dependencies can only be installed with conda.

### Installation
#### Conda
Before installing the package with pip, you need to set up your conda environment.

First, set up a new conda environment:

```bash
conda create -n genworlds python=3.11
conda activate genworlds
```

Then, install the following dependencies:

##### On Windows

You also need to install [Faiss](https://github.com/facebookresearch/faiss)

```bash
conda install -c conda-forge faiss-cpu
```

##### On Mac OS

```bash
conda install scipy
conda install scikit-learn
conda install -c pytorch faiss-cpu
```

#### Pip

After that, you can use pip to install the package:

```bash
pip install genworlds
```

### Run the Rountable example

Start the websocket server and the CLI:

```bash
genworlds-socket-server
genworlds-cli
```

Then in another terminal run the example:

```bash
python use_cases/roundtable/world_setup_tot.py
```

See (use_cases/roundtable/world_setup_tot.py) for the code.

### Usage in your own project
Importing the framework:

```bash
import genworlds
```

See examples for more details.

Before running a simulation, you also need to run the websocket server that will be used for communication between the agents and the world. And also the CLI to visualize what the simulated agents are doing.

```bash
genworlds-socket-server
```

The default port is 7456, but you can change it with the `--port` argument.
You can also set the host with the `--host` argument.

```bash
genworlds-socket-server --port 1234 --host 0.0.0.0
```