import json
import os
import sys
from pathlib import Path

# 让脚本可以直接从 backend 目录运行
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.rag.embedder import embed_texts
from app.rag.loader import load_jobs_from_jsonl
from app.rag.splitter import split_documents
from app.rag.vector_store import FaissVectorStore

DATA_FILE = os.getenv("RAG_SOURCE_FILE", "data/jobs.jsonl")
INDEX_PATH = os.getenv("RAG_INDEX_PATH", "data/vector_index/jobs.faiss")
METADATA_PATH = os.getenv("RAG_METADATA_PATH", "data/vector_index/jobs_meta.json")


def main():
    docs = load_jobs_from_jsonl(DATA_FILE)
    chunked_docs = split_documents(docs, chunk_size=500, overlap=80)

    texts = [doc.jd_text for doc in chunked_docs]
    embeddings = embed_texts(texts)

    metadata = [
        {
            "id": doc.id,
            "title": doc.title,
            "company": doc.company,
            "jd_text": doc.jd_text,
            "source": doc.source,
            "chunk_id": doc.chunk_id,
        }
        for doc in chunked_docs
    ]

    store = FaissVectorStore(index_path=INDEX_PATH, metadata_path=METADATA_PATH)
    store.build(embeddings, metadata)
    store.save()

    print(f"done. docs={len(docs)}, chunks={len(chunked_docs)}")
    print(f"index saved to: {INDEX_PATH}")
    print(f"metadata saved to: {METADATA_PATH}")


if __name__ == "__main__":
    main()