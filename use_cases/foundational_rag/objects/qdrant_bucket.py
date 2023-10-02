import os
import json
from json import JSONDecodeError
from typing import List
import threading

from qdrant_client import QdrantClient
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter

from genworlds.objects.abstracts.object import AbstractObject
from genworlds.events.abstracts.event import AbstractEvent
from genworlds.events.abstracts.action import AbstractAction

# Define the QdrantBucket Object
class QdrantBucket(AbstractObject):
    def __init__(self, id:str, path: str = "./vector_store.qdrant"):
        self.path = path
        self.is_busy = False
        actions = [
            GenerateTextChunkCollection(host_object=self),
            GenerateNERCollection(host_object=self),
            RetrieveChunksBySimilarity(host_object=self),
        ]
        super().__init__(
            name="Qdrant Bucket",
            description="A specialized object designed to manage interactions with the Qdrant vector store. This includes operations like generating text chunk collections, named entity recognition collections, and retrieving chunks by similarity.",
            id=id,
            actions=actions,
        )

class VectorStoreCollectionCreated(AbstractEvent):
    event_type = "vector_store_collection_created"
    description = "Notifies that a new collection has been successfully created in the Qdrant vector store."
    has_been_created: bool = False
    collection_name: str

class VectorStoreCollectionCreationInProcess(AbstractEvent):
    event_type = "vector_store_collection_creation_in_process"
    description = "Notifies that the creation process of the new collection is ongoing. Is a very long process, it can take several minutes to complete."
    collection_name: str

class AgentGeneratesTextChunkCollection(AbstractEvent):
    event_type = "agent_generates_text_chunk_collection"
    description = "Event triggered when an agent needs to generate a collection of text chunks for storage in Qdrant."
    full_text_path: str
    collection_name: str
    num_tokens_chunk_size: int = 500
    metadata: dict = {}

class GenerateTextChunkCollection(AbstractAction):
    trigger_event_class = AgentGeneratesTextChunkCollection
    description = "Action that generates a collection of text chunks for storage in Qdrant."
    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentGeneratesTextChunkCollection):
        # If is not threaded the socket disconnects the client due to timeout (it can not ping the server while working)
        threading.Thread(
            target=self._agent_generates_text_chunk_collection, args=(event,)
        ).start()

    # Function that executes the action of generating a text chunk collection in a qdrant vector store
    def _agent_generates_text_chunk_collection(
        self, event: AgentGeneratesTextChunkCollection
    ):
        # conversion has started message, it will take a while, several minutes before completion
        self.host_object.send_event(
            VectorStoreCollectionCreationInProcess(
            sender_id=self.host_object.id,
            target_id=event.sender_id,
            collection_name=event.collection_name,
            )
        )

        text_splitter = TokenTextSplitter(
            chunk_size=event.num_tokens_chunk_size, chunk_overlap=0
        )

        with open(event.full_text_path, "r") as f:
            joint_text = f.read()

        texts = text_splitter.split_text(joint_text)
        data = [Document(page_content=el) for el in texts]
        documents = data
        text_splitter = CharacterTextSplitter(
            chunk_size=event.num_tokens_chunk_size, chunk_overlap=0
        )
        docs = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        qdrant_chunks = Qdrant.from_documents(
            docs,
            embeddings,
            path=self.host_object.path,
            collection_name=event.collection_name,
        )

        print(
            f"Agent {event.sender_id} has created the collection: {event.collection_name}."
        )
        self.host_object.send_event(
            VectorStoreCollectionCreated(
            sender_id=self.host_object.id,
            target_id=event.sender_id,
            collection_name=event.collection_name,
            has_been_created=True,
            )
        )

class AgentGeneratesNERCollection(AbstractEvent):
    event_type = "agent_generates_ner_collection"
    description = "Event indicating the agent's intent to generate a collection of named entities extracted from a provided text."
    full_text_path: str
    collection_name: str
    num_tokens_chunk_size: int = 500
    metadata: dict = {}
    
class GenerateNERCollection(AbstractAction):
    trigger_event_class = AgentGeneratesNERCollection
    description = "Action that generates a collection of named entities extracted from a provided text."
    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: AgentGeneratesNERCollection):
        # If is not threaded the socket disconnects the client due to timeout (it can not ping the server while working)
        threading.Thread(
            target=self._agent_generates_ner_collection, args=(event,)
        ).start()

    # Function that executes the action of generating a text chunk collection in a qdrant vector store
    def _agent_generates_ner_collection(self, event: AgentGeneratesNERCollection):
        self.host_object.is_busy = True
        self.host_object.send_event(
            VectorStoreCollectionCreationInProcess(
            sender_id=self.host_object.id,
            target_id=event.sender_id,
            collection_name=event.collection_name,
            )
        )
        chat = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")

        sys_prompt = SystemMessage(
            content="""
        Task:

        Extract the named entities and their descriptions from the provided text. An entity in this context refers to a term, concept, or organization that has an explicit explanation or definition in the text.

        Process:

        1. Identify distinct named entities in the text, which its explanation is also contained in the text.
        2. Extract the corresponding explanation or definition for each identified entity.
        3. Present the entity paired with its description in a python dict format {"Entities": [{"Entity1", "desc1"},{"Entity2", "desc2"}, ...]}.
        4. Check that the created python dict has the correct format for being imported with json.loads().
        5. If no explained entities are identified, state "NO ENTITIES EXPLAINED".

        Guidelines:

        - Entities might be names of people, locations, organizations, projects, concepts, or terms used in a specialized context.
        - The description or definition of a named entity typically follows the entity itself and provides clarity about its meaning or context.
        - Ensure to capture the full explanation of the named entity, even if it spans multiple sentences.
        - The descriptions of the entities should make you understand the concept as listed below.
        - Make 100% sure that the final format is a python dict that can be loaded with json.loads() instruction.

        Text:

        """
        )

        with open(event.full_text_path, "r") as f:
            joint_text = f.read()

        text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=0)

        texts = text_splitter.split_text(joint_text)
        data = [Document(page_content=el) for el in texts]

        concepts = []
        for i in range(len(data)):
            text_to_send = data[i].page_content
            message = chat([sys_prompt, HumanMessage(content=text_to_send)])
            if "NO ENTITIES EXPLAINED" in message.content:
                print("No entities found in this chunk of text...")
                continue
            else:
                success = False
                for j in range(10):
                    try:
                        conc = json.loads(message.content)
                        concepts.append(conc)
                        success = True
                        break
                    except JSONDecodeError:
                        print(
                            "The dict generated by the LLM, does not have the proper format. Retrying...."
                        )
                        message = chat([sys_prompt, HumanMessage(content=text_to_send)])
                if not success:
                    print(
                        "It was not possible to format correctly the dict after 10 tries."
                    )
                else:
                    print(f"Successful formatting of chunk {i} after {j} iterations.")

        concepts_unified = {"Entities": []}
        for conc in concepts:
            for el in conc["Entities"]:
                concepts_unified["Entities"].append(el)

        docs = [
            Document(
                page_content=list(concept.keys())[0]
                + ": "
                + concept[str(list(concept.keys())[0])]
            )
            for concept in concepts_unified["Entities"]
        ]
        embeddings = OpenAIEmbeddings()

        qdrant_named_entities = Qdrant.from_documents(
            docs,
            embeddings,
            path=self.host_object.path,  # usually ner
            collection_name=event.collection_name,
        )

        print(
            f"Agent {event.sender_id} has created the collection: {event.collection_name}."
        )
        self.host_object.send_event(
            VectorStoreCollectionCreated(
            sender_id=self.host_object.id,
            target_id=event.sender_id,
            collection_name=event.collection_name,
            has_been_created=True,
            )
        )
        self.is_busy = False

class VectorStoreCollectionRetrieveQuery(AbstractEvent):
    event_type = "agent_sends_query_to_retrieve_chunks"
    description = "Event to signal the retrieval of chunks from a Qdrant collection based on a similarity query."
    collection_name: str
    query: str
    num_chunks: int = 5


class VectorStoreCollectionSimilarChunks(AbstractEvent):
    event_type = "vector_store_collection_similar_chunks"
    description = "Provides a list of text chunks from a Qdrant collection that are similar to a given query."
    collection_name: str
    similar_chunks: List[str]

class RetrieveChunksBySimilarity(AbstractAction):
    trigger_event_class = VectorStoreCollectionRetrieveQuery
    description = "Retrieves a list of text chunks from a Qdrant collection that are similar to a given query."
    def __init__(self, host_object: AbstractObject):
        super().__init__(host_object=host_object)

    def __call__(self, event: VectorStoreCollectionRetrieveQuery):
        embeddings = OpenAIEmbeddings()
        client = QdrantClient(path=self.host_object.path)
        qdrant = Qdrant(
            client=client,
            collection_name=event.collection_name,
            embeddings=embeddings,
        )
        similar_chunks = [
            el.page_content for el in qdrant.similarity_search(event.query, k=10)
        ]

        print(
            f"Agent {event.sender_id} has retrieved: {event.num_chunks} chunks from {event.collection_name}."
        )
        self.host_object.send_event(
            VectorStoreCollectionSimilarChunks(
            sender_id=self.host_object.id,
            target_id=event.sender_id,
            collection_name=event.collection_name,
            similar_chunks=similar_chunks,
            )
        )
