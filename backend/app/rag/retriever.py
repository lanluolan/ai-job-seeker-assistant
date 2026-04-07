from typing import Any, Dict, List

from app.rag.embedder import embed_query
from app.rag.vector_store import FaissVectorStore


class JobRetriever:
    def __init__(self, vector_store: FaissVectorStore):
        self.vector_store = vector_store

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = embed_query(query)
        results = self.vector_store.search(query_embedding, top_k=top_k)

        formatted = []
        for meta, score in results:
            formatted.append(
                {
                    "score": round(score, 4),
                    "id": meta.get("id"),
                    "title": meta.get("title"),
                    "company": meta.get("company"),
                    "jd_text": meta.get("jd_text"),
                    "source": meta.get("source", "manual"),
                    "chunk_id": meta.get("chunk_id"),
                }
            )
        return formatted