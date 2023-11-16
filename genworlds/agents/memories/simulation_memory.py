import json
from typing import List

from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
import qdrant_client
from qdrant_client.http import models as rest
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings

from langchain.docstore.document import Document


class OneLineEventSummarizer:
    def __init__(self, openai_api_key: str, model_name: str = "gpt-3.5-turbo-1106"):
        self.summary_template = """
        This is The last event coming from a web-socket, it is in JSON format:
        {event}
        Summarize what happened in one line.
        """

        self.summary_prompt = PromptTemplate(
            template=self.summary_template,
            input_variables=[
                "event",
            ],
        )

        self.chat = ChatOpenAI(
            temperature=0, model_name=model_name, openai_api_key=openai_api_key
        )
        self.chain = LLMChain(llm=self.chat, prompt=self.summary_prompt)

    def summarize(
        self,
        event: str,
    ) -> str:
        """
        Summarize the event in one line.
        """
        return self.chain.run(event=event)


class FullEventStreamSummarizer:
    def __init__(self, openai_api_key: str, model_name: str = "gpt-3.5-turbo-1106"):
        self.small_summary_template = """
        This is the full event stream coming from a web-socket, it is in JSON format:
        {event_stream}
        Summarize what happened during the event stream in {k} paragraphs.
        
        SUMMARY:
        """

        self.summary_prompt = PromptTemplate(
            template=self.small_summary_template,
            input_variables=[
                "event_stream",
                "k",
            ],
        )

        self.chat = ChatOpenAI(
            temperature=0, model_name=model_name, openai_api_key=openai_api_key
        )
        self.small_summary_chain = LLMChain(llm=self.chat, prompt=self.summary_prompt)

    def summarize(
        self,
        event_stream: List[str],
        k: int = 5,
    ) -> str:
        """
        Summarize the event stream in k paragraphs.
        """
        if len(event_stream) <= 100:
            return self.small_summary_chain.run(event_stream=event_stream, k=k)
        else:
            # needs to be implemented
            return ""


class SimulationMemory:
    """
    Uses NMK Approach to summarize the event stream.
    """

    def __init__(
        self,
        openai_api_key: str,
        model_name: str = "gpt-3.5-turbo-1106",
        n_of_last_events: int = 15,
        n_of_similar_events: int = 5,
        n_of_paragraphs_in_summary: int = 5,
    ):
        self.n_of_last_events = n_of_last_events  # last events
        self.n_of_similar_events = n_of_similar_events  # similar events
        self.n_of_paragraphs_in_summary = (
            n_of_paragraphs_in_summary  # paragraphs in the summary
        )
        self.full_summary = ""

        self.world_events = []
        self.summarized_events = []
        self.one_line_summarizer = OneLineEventSummarizer(
            openai_api_key=openai_api_key, model_name=model_name
        )
        self.full_event_stream_summarizer = FullEventStreamSummarizer(
            openai_api_key=openai_api_key, model_name=model_name
        )

        self.embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

        client = qdrant_client.QdrantClient(location=":memory:")
        client.recreate_collection(
            collection_name="world-events",
            vectors_config={
                "content": rest.VectorParams(
                    distance=rest.Distance.COSINE,
                    size=1536,
                ),
            },
        )
        client.recreate_collection(
            collection_name="summarized-world-events",
            vectors_config={
                "content": rest.VectorParams(
                    distance=rest.Distance.COSINE,
                    size=1536,
                ),
            },
        )
        self.events_db = Qdrant(
            client=client,
            collection_name="world-events",
            embeddings=self.embeddings_model,
        )
        self.summarized_events_db = Qdrant(
            client=client,
            collection_name="summarized-world-events",
            embeddings=self.embeddings_model,
        )

    def add_event(self, event, summarize: bool = False):
        self.world_events.append(event)
        self.events_db.add_documents([Document(page_content=event)])
        if summarize:
            self._add_summarized_event(event)

    def _add_summarized_event(self, event):
        sum_event = self.one_line_summarizer.summarize(event)
        event_as_dict = json.loads(event)
        self.summarized_events.append(event_as_dict["created_at"] + " " + sum_event)
        self.summarized_events_db.add_documents([Document(page_content=sum_event)])

    def create_full_summary(self):
        self.full_summary = self.full_event_stream_summarizer.summarize(
            event_stream=self.world_events, k=self.n_of_paragraphs_in_summary
        )

    def _get_n_last_events(self, summarized: bool = False):
        if summarized:
            events = self.summarized_events[-self.n_of_last_events :]
        else:
            events = self.world_events[-self.n_of_last_events :]
        return events  # [::-1]

    def _get_m_similar_events(self, query: str, summarized: bool = False):
        if self.n_of_similar_events < 1:
            return []

        if summarized:
            m_events = self.summarized_events_db.similarity_search(
                k=self.n_of_similar_events, query=query
            )
            return [el.page_content for el in m_events]
        else:
            m_events = self.events_db.similarity_search(
                k=self.n_of_similar_events, query=query
            )
            return [el.page_content for el in m_events]

    def get_event_stream_memories(self, query: str, summarized: bool = False):
        if len(self.world_events) <= self.n_of_last_events:
            last_events = self._get_n_last_events(summarized=summarized)
            nmk = (
                "\n\n# Your Memories\n\n"
                "## Last events from oldest to most recent\n\n" + "\n".join(last_events)
            )
            return nmk
        last_events = self._get_n_last_events(summarized=summarized)
        # similar_events = self._get_m_similar_events(query=query, summarized=summarized)
        nmk = (
            "\n\n# Your Memories\n\n"
            "## Full Summary\n\n" + self.full_summary
            # + "\n\n## Similar events\n\n"
            # + "\n".join(similar_events)
            + "\n\n## Last events from oldest to most recent\n\n"
            + "\n".join(last_events)
        )
        return nmk
