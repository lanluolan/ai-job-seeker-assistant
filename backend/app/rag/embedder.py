import os
from typing import List

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "EMPTY")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://127.0.0.1:8080/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embeddings-inference")

embeddings_client = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=EMBEDDING_API_KEY,
    base_url=EMBEDDING_BASE_URL,
)


def embed_texts(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    if not texts:
        return []

    vectors: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch_vectors = embeddings_client.embed_documents(batch)
        vectors.extend(batch_vectors)

    return vectors


def embed_query(text: str) -> List[float]:
    if not text.strip():
        return []
    return embeddings_client.embed_query(text)