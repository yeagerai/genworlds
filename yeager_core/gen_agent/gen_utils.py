import math
import faiss
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain.docstore import InMemoryDocstore
from yeager_core.gen_agent.base_gen_agent import GenerativeAgent

def relevance_score_fn(score: float) -> float:
    """Return a similarity score on a scale [0, 1]."""
    # This will differ depending on a few things:
    # - the distance / similarity metric used by the VectorStore
    # - the scale of your embeddings (OpenAI's are unit norm. Many others are not!)
    # This function converts the euclidean norm of normalized embeddings
    # (0 is most similar, sqrt(2) most dissimilar)
    # to a similarity function (0 to 1)
    return 1.0 - score / math.sqrt(2)

def create_new_memory_retriever():
    """Create a new vector store retriever unique to the agent."""
    # Define your embedding model
    embeddings_model = OpenAIEmbeddings()
    # Initialize the vectorstore as empty
    embedding_size = 1536
    index = faiss.IndexFlatL2(embedding_size)
    vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {}, relevance_score_fn=relevance_score_fn)
    return TimeWeightedVectorStoreRetriever(vectorstore=vectorstore, other_score_keys=["importance"], k=15)    

def interview_agent(agent: GenerativeAgent, message: str) -> str:
    """Help the notebook user interact with the agent."""
    new_message = f"{agent.name} says {message}"
    return agent.generate_dialogue_response(new_message)[1]