from dataclasses import dataclass
from typing import Optional


@dataclass
class JobDocument:
    id: str
    title: str
    company: str
    jd_text: str
    source: str = "manual"
    chunk_id: Optional[int] = None