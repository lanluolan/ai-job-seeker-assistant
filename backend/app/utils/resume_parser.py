from pathlib import Path
from typing import Optional

from docx import Document
from pypdf import PdfReader


def read_txt(file_path: str) -> str:
    path = Path(file_path)
    return path.read_text(encoding="utf-8", errors="ignore")


def read_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages_text.append(text)
    return "\n".join(pages_text)


def parse_resume_file(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()

    if suffix == ".txt":
        return read_txt(file_path)
    if suffix == ".docx":
        return read_docx(file_path)
    if suffix == ".pdf":
        return read_pdf(file_path)

    raise ValueError(f"Unsupported resume file type: {suffix}")