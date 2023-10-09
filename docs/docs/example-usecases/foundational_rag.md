---
sidebar_position: 1
---
# Foundational in-house RAG World

:::tip Info

The information hereunder has been extracted from `https://github.com/yeagerai/genworlds/tree/main/use_cases/foundational_rag`. There you have the `.ipynb` file and other supplementary resources.

:::

In this tutorial, we will explore how to create a foundational RAG (Retrieval Augmented Generation) World, laying the groundwork for how we can process our in-house information so that other agents can subsequently process it for various purposes. For example, answering questions based on our own documentation.

For more information about RAG, please visit this blog.

If you haven't followed the steps from the quickstart in the documentation, I recommend doing so before continuing with this tutorial. Also, an initial overview of the essential concepts of the GenWorlds framework is advisable to better understand what we will do next.

## Foundational World Entities
The essential objects we need to build the foundation of our RAG World are:
* **Local Storage Object:** An interface for the agent to access our file system and read documents in `.md`, `.docx`, and `.pdf` formats (for now, without OCR).
* **Qdrant Object (or similar with another vector store):**  Here, we will store some basic processed data structures, such as a text-chunks-collection and a slightly more complex one, like an NER+descriptions collection.
* **Basic Assistant:** This utilizes the previously defined objects, upon user request, to generate various data structures that will subsequently be used by other agents for different purposes.


```python
from time import sleep
from datetime import datetime
from typing import List
import os

from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
```

First, we create a `ChatInterfaceWorld`, which will allow us to connect the world, once launched, to the visual interface of `genworlds-community`, so we can view the interactions more easily than through the notebook. While we can always communicate with the world's agents through the notebook, the GUI simply provides more streamlined visualizations, requires less scrolling, and therefore, makes it easier to understand what is happening in the world. However, if we detect any errors, I always recommend checking the terminal to see the exact traceback.


```python
from genworlds.worlds.concrete.community_chat_interface.world import ChatInterfaceWorld

RAGWorld = ChatInterfaceWorld(
    name="RAGWorld",
    description="""A world simulating the real-world scenario where users seek answers 
    based on processed content from various data sources.""",
    id="rag-world"
)

RAGWorld.launch()
```

    INFO:numexpr.utils:NumExpr defaulting to 8 threads.
    INFO:     Started server process [16772]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:7456 (Press CTRL+C to quit)
    INFO:     ('127.0.0.1', 55914) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [31m[rag-world Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:rag-world Thread:Connected to world socket server ws://127.0.0.1:7456/ws
    

Now, we will begin adding entities to the world; first, we instantiate them, and then we add them to the world. In the event that we modify one and want to test its functionality, the simplest way is through the TestUser by sending the corresponding `trigger_event`. This way, we do not have to wait for the agent to decide to execute the action, and for debugging new features, it is easier.

To view the code for the objects, you can simply go to `objects/`, and there you will find the source files for the objects with the various actions and events of each one.

A valid question would be why the `QdrantBucket` has an action that makes LLM calls and why we don’t do it through the agent? It could also be done through the agent, but since it is a very repetitive prompt, and we are going to have it processing for about 30-40 minutes, and the output format is simply a string (which is not very specific), we can place the action in the object. Although, we could also place it in the agent as long as we launch it in a parallel thread that does not interrupt the natural cycle of `think_n_do`.

### Description and Functionalities of the Local Storage Bucket Object
The `LocalStorageBucket` object aims to manage file conversions and local storage in a specific use case. It comprises of both actions and events to fulfill its functionalities. 

To see the code you can go to `objects/local_storage_bucket.py`

Let's explore the parts of this object:

Object Definition: `LocalStorageBucket`
* Purpose: Consolidate various document types into a single `.txt` file and store it locally.
* Attributes:
    * `storage_path`: Specifies the local path where files are stored.
    * `actions`: Contains instances of possible actions this object can perform. In this case, it is capable of converting documents within a folder to a `.txt` file.
* Initialization: When instantiated, this object receives an id and optionally a storage_path, which defaults to the current directory (`"./"`).

Event: `AgentRequestsFolderConversion`
* Type: `"agent_requests_folder_conversion"`
* Purpose: This event signals a request from an agent to convert all supported document types in a specific folder into a single `.txt` file.
* Attributes:
    * `input_folder_path`: Path to the folder containing documents to be converted.
    * `output_file_path`: Path where the resulting .txt file should be stored.

Event: `FolderConversionCompleted`
* Type: `"folder_conversion_completed"`
* Purpose: To notify the agent when the folder's documents have been successfully converted and stored into a `.txt` file.
* Attributes:
    * `output_txt_path`: The path where the output .txt file is stored.

Action: `ConvertFolderToTxt`
* Trigger Event: `AgentRequestsFolderConversion`
* Purpose: To convert all documents of supported types in a specified folder into a single `.txt` file.
* Execution:
    Upon calling this action, it iterates over all files in the input_folder_path (specified in the triggering event).
    Depending on the file extension (`.md`, `.docx`, or `.pdf`), it reads and extracts text content from each file.
    All extracted texts are concatenated and saved into a single `.txt` file at `output_txt_path`.
    After conversion, it sends a `FolderConversionCompleted` event, notifying the agent about the completion and providing the path of the newly created `.txt` file.

##### Note on Document Types:
* `.md` (Markdown): Reads and extracts text directly.
* `.docx` (Word): Extracts text from each paragraph and concatenates them.
* `.pdf` (PDF): Extracts text from each page and concatenates them.

##### Note on Action Workflow:
When an `AgentRequestsFolderConversion` event is detected, `ConvertFolderToTxt` is triggered, processing documents in the specified folder and then signaling completion through a `FolderConversionCompleted` event.

#### Utilization:
1. Instantiation: `LocalStorageBucket` is created with a unique id and optionally a `storage_path`.
2. Action Triggering: An agent sends an `AgentRequestsFolderConversion` event to instruct the `LocalStorageBucket` to convert documents.
3. Conversion and Notification: Documents are converted, and a `FolderConversionCompleted` event is subsequently issued to inform the agent of task completion and provide the path to the consolidated .txt file.

This object plays a role in managing document conversion, interaction with the agent through events, and local storage management in a foundational example, showcasing basic functionality and event-driven communication within the GenWorlds framework. It's essential to expand on these foundational concepts for implementing advanced functionalities in real-world applications.


```python
from objects.local_storage_bucket import LocalStorageBucket

# Instantiate the Local Storage Bucket
local_storage = LocalStorageBucket(id="local_storage_bucket")

# Incorporate the Local Storage Bucket into the Simulation
RAGWorld.add_object(local_storage)
```

    INFO:     ('127.0.0.1', 55915) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [33m[local_storage_bucket Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:local_storage_bucket Thread:Connected to world socket server ws://127.0.0.1:7456/ws
    

### Description and Functionalities of the Qdrant Bucket Object
The `QdrantBucket` object represents a specialized object designed to manage interactions with a Qdrant vector store. This object is developed to handle several operations like generating text chunk collections, named entity recognition (NER) collections, and retrieving chunks based on similarity. Derived from an abstract object class, `QdrantBucket` is designed to be capable of executing various actions and responding to or triggering events.

Again to look at the code of the `QdrantBucket` object, you can go to `objects/qdrant_bucket.py`

#### Key Components:
* `VectorStoreCollectionCreated` and `VectorStoreCollectionCreationInProcess`:
    - Events that notify about the creation and ongoing creation process of a new collection in the Qdrant vector store.

* `AgentGeneratesTextChunkCollection` and `AgentGeneratesNERCollection`:
    - Events that indicate an agent’s intention to perform actions such as generating a text chunk collection and named entity recognition collection.

* `GenerateTextChunkCollection` and `GenerateNERCollection`:
    - Actions (inherited from AbstractAction) triggered by respective events, which perform operations like creating a text chunk collection and a named entity recognition collection in a threaded manner.

* `VectorStoreCollectionRetrieveQuery` and `VectorStoreCollectionSimilarChunks`:
    - Events to signal a query for retrieving chunks from a Qdrant collection and provide similar chunks from a collection based on a query, respectively.

* `RetrieveChunksBySimilarity`:
    - An action that retrieves a list of text chunks from a Qdrant collection similar to a given query and sends an event with those chunks.

#### Execution Flow Overview:
1. Generating Text Chunk Collection:
    * Trigger: The `AgentGeneratesTextChunkCollection` event.
    * Action: The `GenerateTextChunkCollection` action responds and creates text chunks, possibly store them using Qdrant, and then sends a VectorStoreCollectionCreated event upon completion.

2. Generating NER Collection:
    * Trigger: The `AgentGeneratesNERCollection` event.
    * Action: The `GenerateNERCollection` action responds, extracts named entities and their explanations, converts extracted data to an appropriate format, creates documents and possible embeddings, and finally creates a collection in Qdrant. Then, it sends a `VectorStoreCollectionCreated` event to notify the completion of the process.

3. Retrieving Similar Chunks:
    * Trigger: The `VectorStoreCollectionRetrieveQuery` event.
    * Action: The `RetrieveChunksBySimilarity` action responds, retrieves similar chunks to a given query from a collection using Qdrant, and sends a `VectorStoreCollectionSimilarChunks` event containing the retrieved chunks.

#### Multi-Threading Consideration:
In certain actions (like `GenerateNERCollection`), multi-threading is used to avoid socket disconnection due to timeout while performing long operations. A dedicated function that performs the actual operation is called inside a thread, allowing asynchronous execution and not blocking the main thread.


```python
from objects.qdrant_bucket import QdrantBucket

# Instantiate the QdrantBucket Object
qdrant_bucket = QdrantBucket(id="qdrant_bucket", path="./databases/vector_store.qdrant")

# Incorporate the QdrantBucket into the Simulation
RAGWorld.add_object(qdrant_bucket)
```

    INFO:     ('127.0.0.1', 55916) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [34m[qdrant_bucket Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:qdrant_bucket Thread:Connected to world socket server ws://127.0.0.1:7456/ws
    


```python
from genworlds.utils.test_user import TestUser

# Create a Testing User
test_user = TestUser()
```

    INFO:     ('127.0.0.1', 55917) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [35m[test_user Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:test_user Thread:Connected to world socket server ws://127.0.0.1:7456/ws
    

As we mentioned above, there are some collections that take a long time to build, and therefore we add `VectorStoreCollectionCreated` as a `wakeup_event` so that when a collection finishes building, the agent wakes up and notifies us.


```python
from genworlds.agents.concrete.basic_assistant.utils import generate_basic_assistant
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent
from objects.qdrant_bucket import VectorStoreCollectionCreated


agent_name = "BA"
description = """Agent that helps the user process files and create data structures 
such as vector stores using available objects."""

# Generate a Dummy Agent named BA (Basic Assistant)
ba = generate_basic_assistant(
    agent_name=agent_name, 
    description=description,
    openai_api_key=openai_api_key
)

# We add the vector_store_collection_created event to the wakeup_events dictionary because it can take several minutes to complete
ba.add_wakeup_event(event_class=UserSpeaksWithAgentEvent)
ba.add_wakeup_event(event_class=VectorStoreCollectionCreated)

## Attach BA to the Simulation
RAGWorld.add_agent(ba)
```

    INFO:     ('127.0.0.1', 55918) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [36m[BA Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:BA Thread:Connected to world socket server ws://127.0.0.1:7456/ws
    

    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:14:42.855489", "sender_id": "BA", "target_id": "rag-world"}
    
    ...
    You can find full outputs on GitHub.
    ...

    Agent goes to sleep...
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:14:53.005770", "sender_id": "BA", "target_id": null}
    

Now we have to move the `.md` files from our docs to the `./databases/genworlds-docs` folder, so the agent can access to them and create the different data structures based on the contents of those files.


```python
# import os
# import shutil
# import glob

# # Define paths
# source_path = '../../docs/docs'
# target_path = './databases/genworlds-docs'

# # Ensure the target directory exists, if not create it
# if not os.path.exists(target_path):
#     os.makedirs(target_path)

# # Retrieve all markdown files within and below the source path
# markdown_files = glob.glob(os.path.join(source_path, '**/*.md'), recursive=True)

# # Loop through each markdown file and move it to the target path
# for file_path in markdown_files:
#     # Extract the filename from the file path
#     file_name = os.path.basename(file_path)
    
#     # Create the new path for the file in the target directory
#     new_file_path = os.path.join(target_path, file_name)
    
#     # Ensure no overwriting by checking if a file with the same name already exists in the target path
#     # If it does, modify the filename
#     counter = 1
#     while os.path.exists(new_file_path):
#         name, ext = os.path.splitext(file_name)
#         new_file_path = os.path.join(target_path, f"{name}_{counter}{ext}")
#         counter += 1
    
#     # Copy the file to the new path
#     shutil.copy(file_path, new_file_path)
```


```python
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent

# Format the message that will be sent to the simulation socket
test_msg = """BA Agent, please convert the documents located './databases/genworlds-docs' 
into a single txt and store it as ./databases/genworlds-docs.txt """

message_to_send = UserSpeaksWithAgentEvent(
    sender_id=test_user.id, 
    created_at=datetime.now(),
    message=test_msg, 
    target_id="BA"
).json()

sleep(1)

# Send the message to BA
test_user.socket_client.send_message(message_to_send)
```

```output

    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:15:07.575611", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please convert the documents located './databases/genworlds-docs' \ninto a single txt and store it as ./databases/genworlds-docs.txt "}
    Agent is waking up...

    ...
    You can find full outputs on GitHub.
    ...

    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:15:59.745175", "sender_id": "BA", "target_id": null}
    Agent goes to sleep...
```

Now we are going to use this basic assistant to build the various collections in the vector store, utilizing the GenWorlds documentation and the code repository.


```python
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent

# Format the message that will be sent to the simulation socket
test_msg = """BA Agent, please create a collection named genworlds-text-chunks in the qdrant vectorstore
from the contents of this file ./databases/genworlds-docs.txt """

message_to_send = UserSpeaksWithAgentEvent(
    sender_id=test_user.id, 
    created_at=datetime.now(),
    message=test_msg, 
    target_id="BA"
).json()

sleep(1)

# Send the message to BA
test_user.socket_client.send_message(message_to_send)
```

```output
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:17:13.992159", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-text-chunks in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    Agent is waking up...
    ...
    You can find full outputs on GitHub.
    ...

    Agent goes to sleep...
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:18:37.846122", "sender_id": "BA", "target_id": null}
```

```python
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent

test_msg = """BA Agent, please create a collection named genworlds-ner which extracts Named Entities and its descriptions in the qdrant vectorstore
from the contents of this file ./databases/genworlds-docs.txt """

message_to_send = UserSpeaksWithAgentEvent(
    sender_id=test_user.id, 
    created_at=datetime.now(),
    message=test_msg, 
    target_id="BA"
).json()

sleep(1)

# Send the message to BA
test_user.socket_client.send_message(message_to_send)
```

```output
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:19:14.651682", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-ner which extracts Named Entities and its descriptions in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    ...
    You can find full outputs on GitHub.
    ...

    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:32:14.226670", "sender_id": "BA", "target_id": null}
```

We remind you that this is a foundational and very basic example, simply to see the potential of what can be achieved. Subsequently, by modifying the different actions, adding more objects, more agents—as we will see in future tutorials—the `Q&A Agent` that is connected to these information sources will allow us, for example, to chat with our documentation.
