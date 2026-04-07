import json
from pathlib import Path
from typing import List

from app.rag.schemas import JobDocument


def load_jobs_from_jsonl(file_path: str) -> List[JobDocument]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"jobs file not found: {file_path}")

    docs: List[JobDocument] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            obj = json.loads(line)
            docs.append(
                JobDocument(
                    id=str(obj.get("id", "")),
                    title=obj.get("title", ""),
                    company=obj.get("company", ""),
                    jd_text=obj.get("jd_text", ""),
                    source=obj.get("source", "manual"),
                )
            )
    return docs