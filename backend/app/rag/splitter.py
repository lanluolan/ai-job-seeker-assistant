from typing import List

from app.rag.schemas import JobDocument


def split_text(text: str, chunk_size: int = 500, overlap: int = 80) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)

    return chunks


def split_documents(docs: List[JobDocument], chunk_size: int = 500, overlap: int = 80) -> List[JobDocument]:
    results: List[JobDocument] = []
    for doc in docs:
        chunks = split_text(doc.jd_text, chunk_size=chunk_size, overlap=overlap)
        for i, chunk in enumerate(chunks):
            results.append(
                JobDocument(
                    id=doc.id,
                    title=doc.title,
                    company=doc.company,
                    jd_text=chunk,
                    source=doc.source,
                    chunk_id=i,
                )
            )
    return results