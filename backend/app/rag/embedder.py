import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "EMPTY")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://127.0.0.1:8080/v1")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embeddings-inference")

client = OpenAI(
    api_key=EMBEDDING_API_KEY,
    base_url=EMBEDDING_BASE_URL,
)


def embed_texts(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    if not texts:
        return []

    vectors: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        batch_vectors = [item.embedding for item in resp.data]
        vectors.extend(batch_vectors)

    return vectors


def embed_query(text: str) -> List[float]:
    vectors = embed_texts([text])
    return vectors[0] if vectors else []