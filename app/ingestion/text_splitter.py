"""Split cleaned page text into overlapping chunks, keeping source metadata."""
import re
from dataclasses import dataclass
from pathlib import Path

from app.ingestion.document_loader import PageDoc


@dataclass
class Chunk:
    id: str
    text: str  # includes the "[document label]" prefix
    source: str
    page: int


def doc_label(source: str) -> str:
    """'KA1-Bagalkot_31.1.2011.pdf' -> 'KA1 Bagalkot 31.1.2011'."""
    stem = Path(source).stem
    return re.sub(r"[_\-]+", " ", stem).strip()


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Greedy splitter that prefers paragraph, line, sentence, then word boundaries."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            window = text[start:end]
            for sep in ("\n\n", "\n", ". ", " "):
                cut = window.rfind(sep)
                if cut > chunk_size * 0.5:
                    end = start + cut + len(sep)
                    break
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks


def split_documents(pages: list[PageDoc], chunk_size: int, overlap: int) -> list[Chunk]:
    """Every chunk is prefixed with its document label so district/crop names
    are part of the text that gets embedded and shown to the LLM."""
    chunks: list[Chunk] = []
    for page in pages:
        label = doc_label(page.source)
        for i, piece in enumerate(split_text(page.text, chunk_size, overlap)):
            chunks.append(
                Chunk(
                    id=f"{page.source}-p{page.page}-c{i}",
                    text=f"[{label} | page {page.page}]\n{piece}",
                    source=page.source,
                    page=page.page,
                )
            )
    return chunks
