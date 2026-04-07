import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import faiss
import numpy as np


class FaissVectorStore:
    def __init__(self, index_path: str, metadata_path: str):
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.index = None
        self.metadata: List[Dict[str, Any]] = []

    def build(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]) -> None:
        if not embeddings:
            raise ValueError("embeddings is empty")

        vectors = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(vectors)

        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)

        self.index = index
        self.metadata = metadata

    def save(self) -> None:
        if self.index is None:
            raise ValueError("index is empty")

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        with self.metadata_path.open("w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def load(self) -> None:
        if not self.index_path.exists():
            raise FileNotFoundError(f"index file not found: {self.index_path}")
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"metadata file not found: {self.metadata_path}")

        self.index = faiss.read_index(str(self.index_path))
        with self.metadata_path.open("r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if self.index is None:
            raise ValueError("index is not loaded")

        query_vec = np.array([query_embedding], dtype="float32")
        faiss.normalize_L2(query_vec)

        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            results.append((self.metadata[idx], float(score)))
        return results