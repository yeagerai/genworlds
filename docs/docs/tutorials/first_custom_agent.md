---
sidebar_position: 3
---
# First Custom Agent (Q&A Agent)

:::tip Info

The information hereunder has been extracted from `https://github.com/yeagerai/genworlds/tree/main/use_cases/custom_qna_agent`. There you have the `.ipynb` file and other supplementary resources.

Also before executing this tutorial, you must git clone the repo and execute the `foundational_rag` tutorial.
:::

After following the tutorial for the Foundational in-house RAG World, the natural next step is to want to have a `Q&A Agent` to ask questions about our documentation.

In this tutorial, we will see how we can create a custom agent. This involves adding `ThoughtActions` to the `BasicAssistant` to turn it into a new type of agent, one that adapts to the requirement to answer user questions based on information gathered from the Vector Stores we generated in the previous tutorial.


```python
from time import sleep
from datetime import datetime
from typing import List
import os

from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
```

## Instantiate RAGWorld
Instantiate the old RAGWorld where we have created the vector store collections during the previous tutorial. So all the data structures are there.


```python
from genworlds.worlds.concrete.community_chat_interface.world import ChatInterfaceWorld

RAGWorld = ChatInterfaceWorld(
    name="RAGWorld",
    description="""A world simulating the real-world scenario where users seek answers 
    based on processed content from various data sources.""",
    id="rag-world"
)

RAGWorld.launch()

import sys
sys.path.append("../foundational_rag")
from objects.qdrant_bucket import QdrantBucket

# Instantiate the QdrantBucket Object
qdrant_bucket = QdrantBucket(id="qdrant_bucket", path="../foundational_rag/databases/vector_store.qdrant")

# Incorporate the QdrantBucket into the Simulation
RAGWorld.add_object(qdrant_bucket)
```

```output
    INFO:numexpr.utils:NumExpr defaulting to 8 threads.
    INFO:     Started server process [10584]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://127.0.0.1:7456 (Press CTRL+C to quit)
    INFO:     ('127.0.0.1', 57396) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [31m[rag-world Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:rag-world Thread:Connected to world socket server ws://127.0.0.1:7456/ws
    INFO:     ('127.0.0.1', 57397) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [33m[qdrant_bucket Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:qdrant_bucket Thread:Connected to world socket server ws://127.0.0.1:7456/ws
```

## Custom Agent State
First, we need to create a distinct version of the `AbstractAgentState` to add the variables that we will later use in the specific `Thought` that we are going to construct.


```python
from typing import Type, Optional, List
from genworlds.agents.abstracts.agent_state import AbstractAgentState

class QnAAgentState(AbstractAgentState):
    users_question:Optional[str]
    retrieved_information_from_data_structures: List[str]
```

## Agent Retrieves From Sources Action
Here we add a deterministic action, which simply consists of retrieving data from the vector stores that we created in the previous tutorial. In this way, we collect the text chunks that come from the various vector store collections that we had, and save this information in the `QnAAgentState` that we have designed. This way, it will be accessible from the `Thought`.


```python
from genworlds.events.abstracts.action import AbstractAction
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.objects.abstracts.object import AbstractObject
from objects.qdrant_bucket import VectorStoreCollectionRetrieveQuery, VectorStoreCollectionSimilarChunks

class AgentRetrievesFromSourcesEvent(AbstractEvent):
    event_type = "agent_retrieves_from_sources_event"
    description = "The agent triggers events to the different data structures to retrieve information before answering questions as an expert."
    users_query: str

class AgentRetrievesFromSources(AbstractAction):
    trigger_event_class = AgentRetrievesFromSourcesEvent
    description = "The agent triggers events to the different data structures to retrieve information before answering questions as an expert."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentRetrievesFromSourcesEvent):
        self.host_object.state_manager.state.users_question = event.users_query

        self.host_object.send_event(
            VectorStoreCollectionRetrieveQuery(
                sender_id=self.host_object.id,
                target_id=event.target_id,
                collection_name="genworlds-text-chunks",
                query=event.users_query,
            )
        )

        self.host_object.send_event(
            VectorStoreCollectionRetrieveQuery(
                sender_id=self.host_object.id,
                target_id=event.target_id,
                collection_name="genworlds-ner",
                query=event.users_query,
            )
        )

        sleep(5)

class AddRelevantInfoToState(AbstractAction):
    trigger_event_class = VectorStoreCollectionSimilarChunks
    description = "The agent modifies its state based on the relevant information retrieved from a Vectorstore."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentRetrievesFromSourcesEvent):
        for el in event.similar_chunks:
            self.host_object.state_manager.state.retrieved_information_from_data_structures.append(el)
```

## Create the Custom Thought
Now, we are going to develop the custom thought which will essentially try to answer the user's question based on the text chunks it has received from the different data structures, which are now in the `retrieved_information_from_data_structures` variable of the custom state that we have created.

For this, we use `pydantic.BaseModel` and `LangChain`, and we employ a specific feature of `GPT` models which is function calling. That is, OpenAI enforces that the result we get from `GPT` has the structure of the `pydantic.BaseModel` that we have provided.


```python
from pydantic import BaseModel, Field


from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.openai_functions import (
    create_structured_output_chain,
)


from genworlds.agents.abstracts.agent_state import AbstractAgentState
from genworlds.agents.abstracts.thought import AbstractThought


class JustifiedAnswer(BaseModel):
    """Answers the user's question based on data extracted from different data structures."""

    answer: str = Field(
        ...,
        description="The final answer to the user.",
    )
    rationale: str = Field(
        ...,
        description="The rationale of why this is the correct answer to user's question.",
    )
    references: Optional[List[str]] = Field(
        ..., description="References to documents extracted from metadata."
    )

class AnswerFromSourcesThought(AbstractThought):
    def __init__(
        self,
        agent_state: AbstractAgentState # other thoughts unique init arg, so everything goes through state
    ):
        self.agent_state = agent_state
        self.llm = ChatOpenAI(
            model="gpt-4", openai_api_key=openai_api_key, temperature=0.1
        )

    def run(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are {agent_name}, {agent_description}."),
                (
                    "system",
                    "You are embedded in a simulated world with those properties {agent_world_state}",
                ),
                ("system", "Those are your goals: \n{goals}"),
                (
                    "system",
                    "And this is your current plan to achieve the goals: \n{plan}",
                ),
                (
                    "system",
                    "Here is your memories of all the events that you remember from being in this simulation: \n{memory}",
                ),
                (
                    "system",
                    "This is the last user's question: \n{user_question}",
                ),
                (
                    "system",
                    "This is relevant information related to the user's question: \n{relevant_info}",
                ),
                ("human", "{footer}"),
            ]
        )

        chain = create_structured_output_chain(
            output_schema=JustifiedAnswer.schema(),
            llm=self.llm,
            prompt=prompt,
            verbose=True,
        )
        response = chain.run(
            agent_name=self.agent_state.name,
            agent_description=self.agent_state.description,
            agent_world_state=self.agent_state.host_world_prompt,
            goals=self.agent_state.goals,
            plan=self.agent_state.plan,
            memory=self.agent_state.last_retrieved_memory,
            user_question=self.agent_state.users_question,
            relevant_info=self.agent_state.retrieved_information_from_data_structures,
            footer="""Provide a justified answer to user's question based on the different data structures, the rationale, and references when possible.
            """,
        )
        response = JustifiedAnswer.parse_obj(response)
        return response
```

## Create the Thought Action Answer as Expert
Finally, we are in a position to create the `ThoughtAction`, and thus our `Q&A Agent` will have a new action to respond like an expert to the user's questions.

Note that upon completing the action, we reset all the state values to empty or initial values, so they can be refilled during the user's next question.


```python
from genworlds.agents.abstracts.thought_action import ThoughtAction
from genworlds.events.abstracts.event import AbstractEvent

class AnswerToUserAsExpertTriggerEvent(AbstractEvent):
    event_type = "agent_answers_as_expert_trigger_event"
    description = "An agent answers to the user's question based on retrieved data structures."
    justified_answer: str
    references: Optional[List[str]]

class AnswerToUserAsExpertEvent(AbstractEvent):
    event_type = "agent_answers_as_expert_event"
    description = "An agent answers to the user's question based on retrieved data structures."
    justified_answer: str
    references: Optional[List[str]]

class AnswerToUserAsExpert(ThoughtAction):
    trigger_event_class = AnswerToUserAsExpertTriggerEvent
    required_thoughts = {
        "justified_answer": AnswerFromSourcesThought,
    }
    description = "An agent answers to the user's question based on retrieved data structures."

    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AnswerToUserAsExpertTriggerEvent):
        self.host_object.send_event(
            AnswerToUserAsExpertEvent(
                sender_id=self.host_object.id,
                target_id=event.target_id,
                justified_answer=event.justified_answer,
                references = event.references,
            )
        )
        self.host_object.state_manager.state.users_question = None
        self.host_object.state_manager.state.retrieved_information_from_data_structures = []
        self.host_object.state_manager.state.other_thoughts_filled_parameters["justified_answer"] = ""
```

## The Q&A Agent
Now, we are prepared to create a `Q&A Agent`, which is essentially a `BasicAssistant` but features a custom agent state, and a specific `ThoughtAction`.

Since `AnswerAsExpert` always depends on `AgentRetrievesFromSources`, we will utilize another feature of GenWorlds agents, which is the `ActionChains`.

We will define an action chain that enforces that whenever the agent chooses `AgentRetrievesFromSources` as the next action, `AnswerAsExpert` must necessarily follow. This way, we can follow chains of actions, both deterministic and `ThoughtActions`, without the agent having to constantly decide what the next action will be in processes that always occur the same way, thus reducing the number of errors.


```python
agent_name = "qna_agent"
description = "An agent that helps users with their requests, always answering after reviewing information from available data structures such as vector stores."
answer_as_expert_action_chain = ["qna_agent:AgentRetrievesFromSources", "qna_agent:AnswerToUserAsExpert"]

initial_agent_state = QnAAgentState(
    name=agent_name,
    id=agent_name,
    description=description,
    goals=[
        "Starts waiting and sleeping till the user starts a new question.",
        f"Once {agent_name} receives a user's question, he makes sure to request relevant information from different data structures in order to have all the information before answering as an expert to the user.",
        f"When {agent_name} has all the required information, he answers as an expert based on the information from different data structures.",
        "After sending the response, he waits for the next user question.",
        "If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.",
    ],
    plan=[],
    last_retrieved_memory="",
    other_thoughts_filled_parameters={},
    available_entities=[],
    available_action_schemas={},
    current_action_chain=[],
    host_world_prompt="",
    simulation_memory_persistent_path="./",
    memory_ignored_event_types=(
        "world_sends_available_action_schemas_event",
        "world_sends_available_entities_event",
        "vector_store_collection_similar_chunks",
    ),
    wakeup_event_types=set(),  # fill
    is_asleep=False,
    action_schema_chains=[answer_as_expert_action_chain],
    users_question = None,
    retrieved_information_from_data_structures= [],
)

from genworlds.agents.concrete.basic_assistant.utils import generate_basic_assistant
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent

qna_agent = generate_basic_assistant(
    openai_api_key=openai_api_key,
    agent_name=agent_name,
    description=description,
    initial_agent_state=initial_agent_state,
    action_classes=[AgentRetrievesFromSources, AddRelevantInfoToState, AnswerToUserAsExpert]
)

qna_agent.add_wakeup_event(event_class=UserSpeaksWithAgentEvent)

## Attach Q&A to the World
RAGWorld.add_agent(qna_agent)
```

```output
    INFO:     ('127.0.0.1', 57398) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [34m[qna_agent Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:qna_agent Thread:Connected to world socket server ws://127.0.0.1:7456/ws

   ...
   You can find the complete output on GitHub.
   ... 

    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T12:55:07.779706", "sender_id": "qna_agent", "target_id": "rag-world"}

    Agent goes to sleep...
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T12:56:04.170659", "sender_id": "qna_agent", "target_id": null}
```

## Ask a question to Q&A Agent
Finally, we can now ask the agent specific questions about the framework, and it will respond based on the information it receives from the vector stores. Therefore, this agent responds based on snippets of information from our internal documentation, not solely on what the `GPT` has previously learned during its training phase.


```python
from genworlds.utils.test_user import TestUser

# Create a Testing User
test_user = TestUser()
```

```output
    INFO:     ('127.0.0.1', 57414) - "WebSocket /ws" [accepted]
    INFO:     connection open
    INFO:websocket:Websocket connected
    [36m[test_user Thread] Connected to world socket server ws://127.0.0.1:7456/ws[0m
    INFO:test_user Thread:Connected to world socket server ws://127.0.0.1:7456/ws 
```

```python
from genworlds.worlds.concrete.base.actions import UserSpeaksWithAgentEvent

# Format the message that will be sent to the simulation socket
test_msg = """Do you know what GenWorlds is?"""

message_to_send = UserSpeaksWithAgentEvent(
    sender_id=test_user.id, 
    created_at=datetime.now(),
    message=test_msg, 
    target_id="qna_agent"
).json()

sleep(1)

# Send the message to DCPI
test_user.socket_client.send_message(message_to_send)
```

```output
    {"event_type": "user_speaks_with_agent_event", "description": "The user speaks with an agent.", "summary": null, "created_at": "2023-10-09T12:56:42.104327", "sender_id": "test_user", "target_id": "qna_agent", "message": "Do you know what GenWorlds is?"}
    Agent is waking up...
   ...
   You can find the complete output on GitHub.
   ... 

    [1m> Entering new LLMChain chain...[0m
    Prompt after formatting:
    [32;1m[1;3mSystem: You are qna_agent, An agent that helps users with their requests, always answering after reviewing information from available data structures such as vector stores..
    System: You are embedded in a simulated world with those properties 
    System: Those are your goals: 
    ['Starts waiting and sleeping till the user starts a new question.', "Once qna_agent receives a user's question, he makes sure to request relevant information from different data structures in order to have all the information before answering as an expert to the user.", 'When qna_agent has all the required information, he answers as an expert based on the information from different data structures.', 'After sending the response, he waits for the next user question.', 'If you have been waiting for any object or entity to send you an event for over 30 seconds, you will wait and sleep until you receive a new event.']
    System: And this is your current plan to achieve the goals: 
    []
    System: Here is your memories of all the events that you remember from being in this simulation: 
    
    
    # Your Memories
    
    ## Full Summary
    
    
    
    ## Last events from oldest to most recent
    
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T12:56:45.187067", "sender_id": "qna_agent", "target_id": "rag-world"}
    {"event_type": "agent_sends_query_to_retrieve_chunks", "description": "Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.", "summary": null, "created_at": "2023-10-09T12:57:09.352888", "sender_id": "qna_agent", "target_id": "qdrant_bucket", "collection_name": "genworlds-text-chunks", "query": "Do you know what GenWorlds is?", "num_chunks": 5}
    {"event_type": "agent_sends_query_to_retrieve_chunks", "description": "Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query.", "summary": null, "created_at": "2023-10-09T12:57:09.353933", "sender_id": "qna_agent", "target_id": "qdrant_bucket", "collection_name": "genworlds-ner", "query": "Do you know what GenWorlds is?", "num_chunks": 5}
    {"event_type": "agent_wants_updated_state", "description": "Agent wants to update its state.", "summary": null, "created_at": "2023-10-09T12:57:15.355803", "sender_id": "qna_agent", "target_id": "rag-world"}
    
    
    {"event_type": "agent_answers_as_expert_event", "description": "An agent answers to the user's question based on retrieved data structures.", "summary": null, "created_at": "2023-10-09T12:57:44.798310", "sender_id": "qna_agent", "target_id": "test_user", "justified_answer": "GenWorlds is an event-based communication framework for building multi-agent systems. It provides a platform for creating interactive environments where AI agents asynchronously interact with each other and their environments. GenWorlds utilizes GPT models, which are accessible through `https://platform.openai.com/`. It has a basic abstraction layer that allows you to build agents, objects, and worlds without predefined limits. It also allows you to manage the reliability and accuracy of your system by controlling deterministic and non-deterministic processes. GenWorlds also comes with ready-made agents, objects, and worlds for quick setup while still allowing for customization.", "references": ["https://genworlds.com/"]}
    
    
    System: Those are the available entities that you can choose from: 
    {'rag-world': {'id': 'rag-world', 'entity_type': 'WORLD', 'entity_class': 'ChatInterfaceWorld', 'name': 'RAGWorld', 'description': 'A world simulating the real-world scenario where users seek answers \n    based on processed content from various data sources.'}, 'qna_agent': {'id': 'qna_agent', 'entity_type': 'AGENT', 'entity_class': 'BasicAssistant', 'name': 'qna_agent', 'description': 'An agent that helps users with their requests, always answering after reviewing information from available data structures such as vector stores.'}, 'qdrant_bucket': {'id': 'qdrant_bucket', 'entity_type': 'OBJECT', 'entity_class': 'QdrantBucket', 'name': 'Qdrant Bucket', 'description': 'A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.'}}
    System: Here you have pre-filled parameters coming from your previous thoughts if any: 
    {'justified_answer': ''}
    System: Here is the triggering event schema: 
    {"title": "AgentWantsToSleepEvent", "description": "Helper class that provides a standard way to create an ABC using\ninheritance.", "type": "object", "properties": {"event_type": {"title": "Event Type", "default": "agent_wants_to_sleep", "type": "string"}, "description": {"title": "Description", "default": "The agent wants to sleep. He has to wait for new events. The sender and the target ID is the agent's ID.", "type": "string"}, "summary": {"title": "Summary", "type": "string"}, "created_at": {"title": "Created At", "type": "string", "format": "date-time"}, "sender_id": {"title": "Sender Id", "type": "string"}, "target_id": {"title": "Target Id", "type": "string"}}, "required": ["sender_id"]}
    Human: Fill the parameters of the triggering event based on the previous context that you have about the world.
                [0m
    
    [1m> Finished chain.[0m
    {"event_type": "agent_goes_to_sleep", "description": "The agent is waiting.", "summary": null, "created_at": "2023-10-09T12:58:02.394070", "sender_id": "qna_agent", "target_id": null}
    Agent goes to sleep...
```
