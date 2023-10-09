---
sidebar_position: 2
---
:::tip Info

The information hereunder has been extracted from `https://github.com/yeagerai/genworlds/tree/main/use_cases/foundational_rag`. There you have the `.ipynb` file and other supplementary resources.

:::

# Foundational in-house RAG World
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
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:14:42.859577", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:14:42.870549", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    []
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Last events from oldest to most recent
    
    
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    []
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Last events from oldest to most recent
    
    
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentWantsToSleepEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_wants_to_sleep", "type": "string"}, "description": {"title": "Description", "default": "The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}}, "required": ["sender_id"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
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

    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:15:07.575611", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please convert the documents located './databases/genworlds-docs' \ninto a single txt and store it as ./databases/genworlds-docs.txt "}
    Agent is waking up...
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:15:11.012737", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:15:11.016842", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:15:11.021842", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    []
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:14:53.005770", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:15:07.575611", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please convert the documents located './databases/genworlds-docs' \ninto a single txt and store it as ./databases/genworlds-docs.txt "}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    ['local_storage_bucket:ConvertFolderToTxt', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:14:53.005770", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:15:07.575611", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please convert the documents located './databases/genworlds-docs' \ninto a single txt and store it as ./databases/genworlds-docs.txt "}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentRequestsFolderConversion", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_requests_folder_conversion", "type": "string"}, "description": {"title": "Description", "default": "An agent requests conversion of all supported documents in a specific folder to a single txt file.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}, "input_folder_path": {"title": "Input Folder Path", "type": "string"}, "output_file_path": {"title": "Output File Path", "type": "string"}}, "required": ["summary", "created_at", "sender_id", "target_id", "input_folder_path", "output_file_path"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_requests_folder_conversion", "description": "An agent requests conversion of all supported documents in a specific folder to a single txt file.", "summary": "BA requests conversion of documents in './databases/genworlds-docs' to a single txt file.", "created_at": "2023-10-09T09:15:07.575611", "sender_id": "BA", "target_id": "local_storage_bucket", "input_folder_path": "./databases/genworlds-docs", "output_file_path": "./databases/genworlds-docs.txt"}
    {"event_type": "folder_conversion_completed", "description": "Notifies the agent that the folder has been successfully converted into a txt file.", "summary": null, "created_at": "2023-10-09T09:15:31.121349", "sender_id": "local_storage_bucket", "target_id": "BA", "output_txt_path": "././databases/genworlds-docs.txt"}
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:15:32.068850", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:15:32.071947", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:15:32.077938", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    ['local_storage_bucket:ConvertFolderToTxt', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:14:53.005770", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:15:07.575611", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please convert the documents located './databases/genworlds-docs' \ninto a single txt and store it as ./databases/genworlds-docs.txt "}
    {"event_type": "agent_requests_folder_conversion", "description": "An agent requests conversion of all supported documents in a specific folder to a single txt file.", "summary": "BA requests conversion of documents in './databases/genworlds-docs' to a single txt file.", "created_at": "2023-10-09T09:15:07.575611", "sender_id": "BA", "target_id": "local_storage_bucket", "input_folder_path": "./databases/genworlds-docs", "output_file_path": "./databases/genworlds-docs.txt"}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    ['local_storage_bucket:ConvertFolderToTxt', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:14:53.005770", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:15:07.575611", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please convert the documents located './databases/genworlds-docs' \ninto a single txt and store it as ./databases/genworlds-docs.txt "}
    {"event_type": "agent_requests_folder_conversion", "description": "An agent requests conversion of all supported documents in a specific folder to a single txt file.", "summary": "BA requests conversion of documents in './databases/genworlds-docs' to a single txt file.", "created_at": "2023-10-09T09:15:07.575611", "sender_id": "BA", "target_id": "local_storage_bucket", "input_folder_path": "./databases/genworlds-docs", "output_file_path": "./databases/genworlds-docs.txt"}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentSpeaksWithUserTriggerEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_speaks_with_user_trigger_event", "type": "string"}, "description": {"title": "Description", "default": "An agent speaks with the user.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}, "message": {"title": "Message", "type": "string"}}, "required": ["sender_id", "message"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:15:48.357762", "sender_id": "BA", "target_id": null, "message": "The documents located in './databases/genworlds-docs' have been successfully converted into a single txt file and stored as './databases/genworlds-docs.txt'"}
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:15:49.359434", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:15:49.361597", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:15:49.364548", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    ['local_storage_bucket:ConvertFolderToTxt', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:14:53.005770", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:15:07.575611", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please convert the documents located './databases/genworlds-docs' \ninto a single txt and store it as ./databases/genworlds-docs.txt "}
    {"event_type": "agent_requests_folder_conversion", "description": "An agent requests conversion of all supported documents in a specific folder to a single txt file.", "summary": "BA requests conversion of documents in './databases/genworlds-docs' to a single txt file.", "created_at": "2023-10-09T09:15:07.575611", "sender_id": "BA", "target_id": "local_storage_bucket", "input_folder_path": "./databases/genworlds-docs", "output_file_path": "./databases/genworlds-docs.txt"}
    {"event_type": "folder_conversion_completed", "description": "Notifies the agent that the folder has been successfully converted into a txt file.", "summary": null, "created_at": "2023-10-09T09:15:31.121349", "sender_id": "local_storage_bucket", "target_id": "BA", "output_txt_path": "././databases/genworlds-docs.txt"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:15:48.357762", "sender_id": "BA", "target_id": null, "message": "The documents located in './databases/genworlds-docs' have been successfully converted into a single txt file and stored as './databases/genworlds-docs.txt'"}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    []
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:14:53.005770", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:15:07.575611", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please convert the documents located './databases/genworlds-docs' \ninto a single txt and store it as ./databases/genworlds-docs.txt "}
    {"event_type": "agent_requests_folder_conversion", "description": "An agent requests conversion of all supported documents in a specific folder to a single txt file.", "summary": "BA requests conversion of documents in './databases/genworlds-docs' to a single txt file.", "created_at": "2023-10-09T09:15:07.575611", "sender_id": "BA", "target_id": "local_storage_bucket", "input_folder_path": "./databases/genworlds-docs", "output_file_path": "./databases/genworlds-docs.txt"}
    {"event_type": "folder_conversion_completed", "description": "Notifies the agent that the folder has been successfully converted into a txt file.", "summary": null, "created_at": "2023-10-09T09:15:31.121349", "sender_id": "local_storage_bucket", "target_id": "BA", "output_txt_path": "././databases/genworlds-docs.txt"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:15:48.357762", "sender_id": "BA", "target_id": null, "message": "The documents located in './databases/genworlds-docs' have been successfully converted into a single txt file and stored as './databases/genworlds-docs.txt'"}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentWantsToSleepEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_wants_to_sleep", "type": "string"}, "description": {"title": "Description", "default": "The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}}, "required": ["sender_id"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:15:59.745175", "sender_id": "BA", "target_id": null}
    Agent goes to sleep...
    

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

    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:17:13.992159", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-text-chunks in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    Agent is waking up...
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:17:16.777306", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:17:16.780321", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:17:16.784374", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    []
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_requests_folder_conversion", "description": "An agent requests conversion of all supported documents in a specific folder to a single txt file.", "summary": "BA requests conversion of documents in './databases/genworlds-docs' to a single txt file.", "created_at": "2023-10-09T09:15:07.575611", "sender_id": "BA", "target_id": "local_storage_bucket", "input_folder_path": "./databases/genworlds-docs", "output_file_path": "./databases/genworlds-docs.txt"}
    {"event_type": "folder_conversion_completed", "description": "Notifies the agent that the folder has been successfully converted into a txt file.", "summary": null, "created_at": "2023-10-09T09:15:31.121349", "sender_id": "local_storage_bucket", "target_id": "BA", "output_txt_path": "././databases/genworlds-docs.txt"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:15:48.357762", "sender_id": "BA", "target_id": null, "message": "The documents located in './databases/genworlds-docs' have been successfully converted into a single txt file and stored as './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:15:59.745175", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:17:13.992159", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-text-chunks in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    ['qdrant_bucket:GenerateTextChunkCollection', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_requests_folder_conversion", "description": "An agent requests conversion of all supported documents in a specific folder to a single txt file.", "summary": "BA requests conversion of documents in './databases/genworlds-docs' to a single txt file.", "created_at": "2023-10-09T09:15:07.575611", "sender_id": "BA", "target_id": "local_storage_bucket", "input_folder_path": "./databases/genworlds-docs", "output_file_path": "./databases/genworlds-docs.txt"}
    {"event_type": "folder_conversion_completed", "description": "Notifies the agent that the folder has been successfully converted into a txt file.", "summary": null, "created_at": "2023-10-09T09:15:31.121349", "sender_id": "local_storage_bucket", "target_id": "BA", "output_txt_path": "././databases/genworlds-docs.txt"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:15:48.357762", "sender_id": "BA", "target_id": null, "message": "The documents located in './databases/genworlds-docs' have been successfully converted into a single txt file and stored as './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:15:59.745175", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:17:13.992159", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-text-chunks in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentGeneratesTextChunkCollection", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_generates_text_chunk_collection", "type": "string"}, "description": {"title": "Description", "default": "Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}, "full_text_path": {"title": "Full Text Path", "type": "string"}, "collection_name": {"title": "Collection Name", "type": "string"}, "num_tokens_chunk_size": {"title": "Num Tokens Chunk Size", "default": 500, "type": "integer"}, "metadata": {"title": "Metadata", "default": {}, "type": "object"}}, "required": ["summary", "created_at", "sender_id", "target_id", "full_text_path", "collection_name"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_generates_text_chunk_collection", "description": "Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.", "summary": "BA generates a text chunk collection named 'genworlds-text-chunks' from the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:17:14.992159", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-text-chunks", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:17:44.014049", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-text-chunks"}
    

    WARNING:langchain.text_splitter:Created a chunk of size 575, which is longer than the specified 500
    WARNING:langchain.text_splitter:Created a chunk of size 667, which is longer than the specified 500
    WARNING:langchain.text_splitter:Created a chunk of size 598, which is longer than the specified 500
    WARNING:langchain.text_splitter:Created a chunk of size 651, which is longer than the specified 500
    WARNING:langchain.text_splitter:Created a chunk of size 559, which is longer than the specified 500
    WARNING:langchain.text_splitter:Created a chunk of size 591, which is longer than the specified 500
    WARNING:langchain.text_splitter:Created a chunk of size 545, which is longer than the specified 500
    WARNING:langchain.text_splitter:Created a chunk of size 640, which is longer than the specified 500
    

    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:17:45.012761", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:17:45.016830", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:17:45.022830", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    ['qdrant_bucket:GenerateTextChunkCollection', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "folder_conversion_completed", "description": "Notifies the agent that the folder has been successfully converted into a txt file.", "summary": null, "created_at": "2023-10-09T09:15:31.121349", "sender_id": "local_storage_bucket", "target_id": "BA", "output_txt_path": "././databases/genworlds-docs.txt"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:15:48.357762", "sender_id": "BA", "target_id": null, "message": "The documents located in './databases/genworlds-docs' have been successfully converted into a single txt file and stored as './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:15:59.745175", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:17:13.992159", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-text-chunks in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    {"event_type": "agent_generates_text_chunk_collection", "description": "Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.", "summary": "BA generates a text chunk collection named 'genworlds-text-chunks' from the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:17:14.992159", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-text-chunks", "num_tokens_chunk_size": 500, "metadata": {}}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    Agent BA has created the collection: genworlds-text-chunks.
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:17:48.681991", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-text-chunks"}
    Agent is waking up...
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    ['qdrant_bucket:GenerateTextChunkCollection', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "folder_conversion_completed", "description": "Notifies the agent that the folder has been successfully converted into a txt file.", "summary": null, "created_at": "2023-10-09T09:15:31.121349", "sender_id": "local_storage_bucket", "target_id": "BA", "output_txt_path": "././databases/genworlds-docs.txt"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:15:48.357762", "sender_id": "BA", "target_id": null, "message": "The documents located in './databases/genworlds-docs' have been successfully converted into a single txt file and stored as './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:15:59.745175", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:17:13.992159", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-text-chunks in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    {"event_type": "agent_generates_text_chunk_collection", "description": "Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.", "summary": "BA generates a text chunk collection named 'genworlds-text-chunks' from the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:17:14.992159", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-text-chunks", "num_tokens_chunk_size": 500, "metadata": {}}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentSpeaksWithUserTriggerEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_speaks_with_user_trigger_event", "type": "string"}, "description": {"title": "Description", "default": "An agent speaks with the user.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}, "message": {"title": "Message", "type": "string"}}, "required": ["sender_id", "message"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:01.870939", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-text-chunks' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:18:02.872718", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:18:02.876357", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:18:02.883364", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    ['qdrant_bucket:GenerateTextChunkCollection', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:17:13.992159", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-text-chunks in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    {"event_type": "agent_generates_text_chunk_collection", "description": "Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.", "summary": "BA generates a text chunk collection named 'genworlds-text-chunks' from the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:17:14.992159", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-text-chunks", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:17:44.014049", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-text-chunks"}
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:17:48.681991", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-text-chunks"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:01.870939", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-text-chunks' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    ['BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:17:13.992159", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-text-chunks in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    {"event_type": "agent_generates_text_chunk_collection", "description": "Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.", "summary": "BA generates a text chunk collection named 'genworlds-text-chunks' from the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:17:14.992159", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-text-chunks", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:17:44.014049", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-text-chunks"}
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:17:48.681991", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-text-chunks"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:01.870939", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-text-chunks' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentSpeaksWithUserTriggerEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_speaks_with_user_trigger_event", "type": "string"}, "description": {"title": "Description", "default": "An agent speaks with the user.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}, "message": {"title": "Message", "type": "string"}}, "required": ["sender_id", "message"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:21.833286", "sender_id": "BA", "target_id": null, "message": "The collection 'genworlds-text-chunks' has been successfully created in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:18:22.835726", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:18:22.839796", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:18:22.843439", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    ['BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_generates_text_chunk_collection", "description": "Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.", "summary": "BA generates a text chunk collection named 'genworlds-text-chunks' from the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:17:14.992159", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-text-chunks", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:17:44.014049", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-text-chunks"}
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:17:48.681991", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-text-chunks"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:01.870939", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-text-chunks' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:21.833286", "sender_id": "BA", "target_id": null, "message": "The collection 'genworlds-text-chunks' has been successfully created in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    []
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_generates_text_chunk_collection", "description": "Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.", "summary": "BA generates a text chunk collection named 'genworlds-text-chunks' from the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:17:14.992159", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-text-chunks", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:17:44.014049", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-text-chunks"}
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:17:48.681991", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-text-chunks"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:01.870939", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-text-chunks' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:21.833286", "sender_id": "BA", "target_id": null, "message": "The collection 'genworlds-text-chunks' has been successfully created in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentWantsToSleepEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_wants_to_sleep", "type": "string"}, "description": {"title": "Description", "default": "The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}}, "required": ["sender_id"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    Agent goes to sleep...
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:18:37.846122", "sender_id": "BA", "target_id": null}
    


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

    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:19:14.651682", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-ner which extracts Named Entities and its descriptions in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    Agent is waking up...
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:19:17.862271", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:19:17.865342", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:19:17.868340", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    []
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:17:48.681991", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-text-chunks"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:01.870939", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-text-chunks' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:21.833286", "sender_id": "BA", "target_id": null, "message": "The collection 'genworlds-text-chunks' has been successfully created in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:18:37.846122", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:19:14.651682", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-ner which extracts Named Entities and its descriptions in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    ['qdrant_bucket:GenerateNERCollection', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:17:48.681991", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-text-chunks"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:01.870939", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-text-chunks' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:21.833286", "sender_id": "BA", "target_id": null, "message": "The collection 'genworlds-text-chunks' has been successfully created in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:18:37.846122", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:19:14.651682", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-ner which extracts Named Entities and its descriptions in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentGeneratesNERCollection", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_generates_ner_collection", "type": "string"}, "description": {"title": "Description", "default": "Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}, "full_text_path": {"title": "Full Text Path", "type": "string"}, "collection_name": {"title": "Collection Name", "type": "string"}, "num_tokens_chunk_size": {"title": "Num Tokens Chunk Size", "default": 500, "type": "integer"}, "metadata": {"title": "Metadata", "default": {}, "type": "object"}}, "required": ["summary", "created_at", "sender_id", "target_id", "full_text_path", "collection_name"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_generates_ner_collection", "description": "Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.", "summary": "BA Agent is generating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:19:14.651682", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-ner", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:19:41.811204", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-ner"}
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:19:42.810481", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:19:42.813697", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:19:42.816699", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    ['qdrant_bucket:GenerateNERCollection', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:01.870939", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-text-chunks' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:21.833286", "sender_id": "BA", "target_id": null, "message": "The collection 'genworlds-text-chunks' has been successfully created in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:18:37.846122", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:19:14.651682", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-ner which extracts Named Entities and its descriptions in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    {"event_type": "agent_generates_ner_collection", "description": "Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.", "summary": "BA Agent is generating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:19:14.651682", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-ner", "num_tokens_chunk_size": 500, "metadata": {}}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    ['qdrant_bucket:GenerateNERCollection', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:01.870939", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-text-chunks' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:18:21.833286", "sender_id": "BA", "target_id": null, "message": "The collection 'genworlds-text-chunks' has been successfully created in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:18:37.846122", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:19:14.651682", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-ner which extracts Named Entities and its descriptions in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    {"event_type": "agent_generates_ner_collection", "description": "Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.", "summary": "BA Agent is generating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:19:14.651682", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-ner", "num_tokens_chunk_size": 500, "metadata": {}}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentSpeaksWithUserTriggerEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_speaks_with_user_trigger_event", "type": "string"}, "description": {"title": "Description", "default": "An agent speaks with the user.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}, "message": {"title": "Message", "type": "string"}}, "required": ["sender_id", "message"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:19:58.435836", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:19:59.437627", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:19:59.437627", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:19:59.438631", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    ['qdrant_bucket:GenerateNERCollection', 'BA:AgentSpeaksWithUser', 'BA:AgentGoesToSleep']
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:18:37.846122", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:19:14.651682", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-ner which extracts Named Entities and its descriptions in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    {"event_type": "agent_generates_ner_collection", "description": "Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.", "summary": "BA Agent is generating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:19:14.651682", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-ner", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:19:41.811204", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-ner"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:19:58.435836", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    The dict generated by the LLM, does not have the proper format. Retrying....
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    []
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:18:37.846122", "sender_id": "BA", "target_id": null}
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T09:19:14.651682", "sender_id": "test_user", "target_id": "BA", "message": "BA Agent, please create a collection named genworlds-ner which extracts Named Entities and its descriptions in the qdrant vectorstore\nfrom the contents of this file ./databases/genworlds-docs.txt "}
    {"event_type": "agent_generates_ner_collection", "description": "Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.", "summary": "BA Agent is generating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:19:14.651682", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-ner", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:19:41.811204", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-ner"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:19:58.435836", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentWantsToSleepEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_wants_to_sleep", "type": "string"}, "description": {"title": "Description", "default": "The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}}, "required": ["sender_id"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:20:15.719954", "sender_id": "BA", "target_id": null}
    Agent goes to sleep...
    The dict generated by the LLM, does not have the proper format. Retrying....
    The dict generated by the LLM, does not have the proper format. Retrying....
    Successful formatting of chunk 0 after 3 iterations.
    Successful formatting of chunk 1 after 0 iterations.
    The dict generated by the LLM, does not have the proper format. Retrying....
    The dict generated by the LLM, does not have the proper format. Retrying....
    Successful formatting of chunk 2 after 2 iterations.
    The dict generated by the LLM, does not have the proper format. Retrying....
    Successful formatting of chunk 3 after 1 iterations.
    Successful formatting of chunk 4 after 0 iterations.
    Successful formatting of chunk 5 after 0 iterations.
    Successful formatting of chunk 6 after 0 iterations.
    Successful formatting of chunk 7 after 0 iterations.
    Successful formatting of chunk 8 after 0 iterations.
    The dict generated by the LLM, does not have the proper format. Retrying....
    The dict generated by the LLM, does not have the proper format. Retrying....
    Successful formatting of chunk 9 after 2 iterations.
    Successful formatting of chunk 10 after 0 iterations.
    Successful formatting of chunk 11 after 0 iterations.
    Successful formatting of chunk 12 after 0 iterations.
    The dict generated by the LLM, does not have the proper format. Retrying....
    Successful formatting of chunk 13 after 1 iterations.
    Agent BA has created the collection: genworlds-ner.
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:31:58.993537", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-ner"}
    Agent is waking up...
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T09:32:00.992696", "sender_id": "BA", "target_id": "rag-world"}
    {"event_type": "world_sends_available_entities_event", "description": "Send available entities.", "summary": null, "created_at": "2023-10-09T09:32:00.992696", "sender_id": "rag-world", "target_id": "BA", "available_entities": {"rag-world": {"id": "rag-world", "entity_type": "WORLD", "entity_class": "ChatInterfaceWorld", "name": "RAGWorld", "description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources."}, "BA": {"id": "BA", "entity_type": "AGENT", "entity_class": "BasicAssistant", "name": "BA", "description": "Agent that helps the user process files and create data structures \nsuch as vector stores using available objects."}, "local_storage_bucket": {"id": "local_storage_bucket", "entity_type": "OBJECT", "entity_class": "LocalStorageBucket", "name": "LocalStorage Bucket", "description": "Object used to consolidate various document types into a single .txt file and store it locally."}, "qdrant_bucket": {"id": "qdrant_bucket", "entity_type": "OBJECT", "entity_class": "QdrantBucket", "name": "Qdrant Bucket", "description": "A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity."}}}
    {"event_type": "world_sends_available_action_schemas_event", "description": "The world sends the possible action schemas to all the agents.", "summary": null, "created_at": "2023-10-09T09:32:00.994026", "sender_id": "rag-world", "target_id": null, "world_name": "RAGWorld", "world_description": "A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.", "available_action_schemas": {"local_storage_bucket:ConvertFolderToTxt": "Converts all supported documents in a specific folder to a single txt file.|agent_requests_folder_conversion|{\"title\": \"AgentRequestsFolderConversion\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_requests_folder_conversion\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent requests conversion of all supported documents in a specific folder to a single txt file.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"input_folder_path\": {\"title\": \"Input Folder Path\", \"type\": \"string\"}, \"output_file_path\": {\"title\": \"Output File Path\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"input_folder_path\", \"output_file_path\"]}", "qdrant_bucket:GenerateTextChunkCollection": "Action that generates a collection of text chunks for storage in Qdrant.|agent_generates_text_chunk_collection|{\"title\": \"AgentGeneratesTextChunkCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_text_chunk_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:GenerateNERCollection": "Action that generates a collection of named entities extracted from a provided text.|agent_generates_ner_collection|{\"title\": \"AgentGeneratesNERCollection\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_generates_ner_collection\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"full_text_path\": {\"title\": \"Full Text Path\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"num_tokens_chunk_size\": {\"title\": \"Num Tokens Chunk Size\", \"default\": 500, \"type\": \"integer\"}, \"metadata\": {\"title\": \"Metadata\", \"default\": {}, \"type\": \"object\"}}, \"required\": [\"sender_id\", \"full_text_path\", \"collection_name\"]}", "qdrant_bucket:RetrieveChunksBySimilarity": "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.|agent_sends_query_to_retrieve_chunks|{\"title\": \"VectorStoreCollectionRetrieveQuery\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_sends_query_to_retrieve_chunks\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"collection_name\": {\"title\": \"Collection Name\", \"type\": \"string\"}, \"query\": {\"title\": \"Query\", \"type\": \"string\"}, \"num_chunks\": {\"title\": \"Num Chunks\", \"default\": 5, \"type\": \"integer\"}}, \"required\": [\"sender_id\", \"collection_name\", \"query\"]}", "BA:UpdateAgentAvailableEntities": "Update the available entities in the agent's state.|world_sends_available_entities_event|{\"title\": \"WorldSendsAvailableEntitiesEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_entities_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"Send available entities.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"available_entities\": {\"title\": \"Available Entities\", \"type\": \"object\"}}, \"required\": [\"sender_id\", \"available_entities\"]}", "BA:UpdateAgentAvailableActionSchemas": "Update the available action schemas in the agent's state.|world_sends_available_action_schemas_event|{\"title\": \"WorldSendsAvailableActionSchemasEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"world_sends_available_action_schemas_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The world sends the possible action schemas to all the agents.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"world_name\": {\"title\": \"World Name\", \"type\": \"string\"}, \"world_description\": {\"title\": \"World Description\", \"type\": \"string\"}, \"available_action_schemas\": {\"title\": \"Available Action Schemas\", \"type\": \"object\", \"additionalProperties\": {\"type\": \"string\"}}}, \"required\": [\"sender_id\", \"world_name\", \"world_description\", \"available_action_schemas\"]}", "BA:AgentGoesToSleep": "The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.|agent_wants_to_sleep|{\"title\": \"AgentWantsToSleepEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_wants_to_sleep\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}}, \"required\": [\"sender_id\"]}", "BA:AgentSpeaksWithUser": "An agent speaks with the user.|agent_speaks_with_user_trigger_event|{\"title\": \"AgentSpeaksWithUserTriggerEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_user_trigger_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with the user.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}", "BA:AgentSpeaksWithAgent": "An agent speaks with another agent.|agent_speaks_with_agent_event|{\"title\": \"AgentSpeaksWithAgentEvent\", \"description\": \"Helper class that provides a standard way to create an ABC using\\ninheritance.\", \"type\": \"object\", \"properties\": {\"event_type\": {\"title\": \"Event Type\", \"default\": \"agent_speaks_with_agent_event\", \"type\": \"string\"}, \"description\": {\"title\": \"Description\", \"default\": \"An agent speaks with another agent.\", \"type\": \"string\"}, \"summary\": {\"title\": \"Summary\", \"type\": \"string\"}, \"created_at\": {\"title\": \"Created At\", \"type\": \"string\", \"format\": \"date-time\"}, \"sender_id\": {\"title\": \"Sender Id\", \"type\": \"string\"}, \"target_id\": {\"title\": \"Target Id\", \"type\": \"string\"}, \"message\": {\"title\": \"Message\", \"type\": \"string\"}}, \"required\": [\"sender_id\", \"message\"]}"}}
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    
    System: You are embedded in a simulated world with those properties 
    
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    
    System: And this is your current plan to achieve the goals: 
    []
    
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_generates_ner_collection", "description": "Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.", "summary": "BA Agent is generating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:19:14.651682", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-ner", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:19:41.811204", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-ner"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:19:58.435836", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:20:15.719954", "sender_id": "BA", "target_id": null}
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:31:58.993537", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-ner"}
    
    System: Those are the available actions that you can choose from: 
    ## Available Actions: 
    
    Action Name: local_storage_bucket:ConvertFolderToTxt
    Action Description: Converts all supported documents in a specific folder to a single txt file.
    
    Action Name: qdrant_bucket:GenerateTextChunkCollection
    Action Description: Action that generates a collection of text chunks for storage in Qdrant.
    
    Action Name: qdrant_bucket:GenerateNERCollection
    Action Description: Action that generates a collection of named entities extracted from a provided text.
    
    Action Name: qdrant_bucket:RetrieveChunksBySimilarity
    Action Description: Retrieves a list of text chunks from a Qdrant collection that are similar to a given query.
    
    Action Name: BA:UpdateAgentAvailableEntities
    Action Description: Update the available entities in the agent's state.
    
    Action Name: BA:UpdateAgentAvailableActionSchemas
    Action Description: Update the available action schemas in the agent's state.
    
    Action Name: BA:AgentGoesToSleep
    Action Description: The agent goes to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.
    
    Action Name: BA:AgentSpeaksWithUser
    Action Description: An agent speaks with the user.
    
    Action Name: BA:AgentSpeaksWithAgent
    Action Description: An agent speaks with another agent.
    
    
    
    Human: Select the next action which must be a value of the available actions that you can choose from based on previous context.
    Also select whether the action is valid or not, and if not, why.
    And finally, state a new updated plan that you want to execute to achieve your goals. If your next action is going to sleep, then you don't need to state a new plan.
                
    [0m
    
    [1m> Finished chain.[0m
    
    
    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are BA, Agent that helps the user process files and create data structures 
    such as vector stores using available objects..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeps till the user starts a new question.', "Once BA receives a user's question, he makes sure to have all the information before sending the answer to the user.", 'When BA has all the required information, he speaks to the user with the results through the agent_speaks_with_user_event.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    []
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_generates_ner_collection", "description": "Event indicating the agent's intent to generate a collection of named entities extracted from a provided text.", "summary": "BA Agent is generating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'", "created_at": "2023-10-09T09:19:14.651682", "sender_id": "BA", "target_id": "qdrant_bucket", "full_text_path": "./databases/genworlds-docs.txt", "collection_name": "genworlds-ner", "num_tokens_chunk_size": 500, "metadata": {}}
    {"event_type": "vector_store_collection_creation_in_process", "description": "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete.", "summary": null, "created_at": "2023-10-09T09:19:41.811204", "sender_id": "qdrant_bucket", "target_id": "BA", "collection_name": "genworlds-ner"}
    {"event_type": "agent_speaks_with_user_event", "description": "An agent speaks with the user.", "summary": null, "created_at": "2023-10-09T09:19:58.435836", "sender_id": "BA", "target_id": null, "message": "I am currently creating a collection named 'genworlds-ner' in the qdrant vectorstore from the contents of the file './databases/genworlds-docs.txt'"}
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:20:15.719954", "sender_id": "BA", "target_id": null}
    {"event_type": "vector_store_collection_created", "description": "Notifies that a new collection has been successfully created in the Qdrant vector store.", "summary": null, "created_at": "2023-10-09T09:31:58.993537", "sender_id": "qdrant_bucket", "target_id": "BA", "has_been_created": true, "collection_name": "genworlds-ner"}
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'BA': {'id': 'BA', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'BA', 'description': 'Agent that helps the user process files and create data structures \nsuch as vector stores using available objects.'}, 'local_storage_bucket': {'id': 'local_storage_bucket', 'entity_type': 'OBJECT', 'entity_class': 'LocalStorageBucket', 'name': 'LocalStorage Bucket', 'description': 'Object used to consolidate various document types into a single .txt file and store it locally.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {}
    System: Here is the triggering event schema: 
    {"title": "AgentWantsToSleepEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_wants_to_sleep", "type": "string"}, "description": {"title": "Description", "default": "The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}}, "required": ["sender_id"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    Agent goes to sleep...
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T09:32:14.226670", "sender_id": "BA", "target_id": null}
    

We remind you that this is a foundational and very basic example, simply to see the potential of what can be achieved. Subsequently, by modifying the different actions, adding more objects, more agents—as we will see in future tutorials—the `Q&A Agent` that is connected to these information sources will allow us, for example, to chat with our documentation.
