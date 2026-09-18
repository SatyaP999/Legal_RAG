import os
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings


load_dotenv()
EMBEDDINGS_KEY = os.getenv("AI_CREDITS_API_KEY", "")

def get_embeddings():
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=EMBEDDINGS_KEY,
        base_url="https://api.aicredits.in/v1",
    )

def get_vectorstore(
        collection_name: str,
        persistent_directory: str = "./chroma_db"
):
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=persistent_directory,
        collection_metadata={
            "hnsw:space": "cosine"
        }
    )


    