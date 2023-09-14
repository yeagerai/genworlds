# DB migration
def run_chroma_to_qdrant_migration(
    collections: list[str], chroma_db_path: str, qdrant_db_path: str
):
    import os
    import chromadb
    from dotenv import load_dotenv
    from langchain.vectorstores import Chroma, Qdrant
    from langchain.embeddings import OpenAIEmbeddings
    from qdrant_client.http import models as rest
    from qdrant_client import QdrantClient

    load_dotenv(dotenv_path=".env")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    ABS_PATH = os.path.dirname(os.path.abspath(__file__))

    embeddings_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

    qdrant_client = QdrantClient(path=qdrant_db_path)

    for collection_name in collections:
        print("Migrating collection", collection_name)
        client_settings = chromadb.config.Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=chroma_db_path,
            anonymized_telemetry=False,
        )

        collection = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings_model,
            client_settings=client_settings,
            persist_directory=chroma_db_path,
        )

        items = collection._collection.get(
            include=["embeddings", "metadatas", "documents"]
        )

        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=rest.VectorParams(
                distance=rest.Distance.COSINE,
                size=1536,
            ),
        )

        CONTENT_KEY = "page_content"
        METADATA_KEY = "metadata"

        qdrant_client.upsert(
            collection_name=collection_name,
            points=rest.Batch.construct(
                ids=items["ids"],
                vectors=items["embeddings"],
                payloads=Qdrant._build_payloads(
                    items["documents"], items["metadatas"], CONTENT_KEY, METADATA_KEY
                ),
            ),
        )

    print("Done")
