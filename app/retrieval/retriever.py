"""Query -> relevant chunks, with a relevance threshold (the diamond in the flowchart).

Retrieval = metadata filter (if the question names a district/document)
          + vector search over a wide candidate pool
          + keyword re-ranking
          + distance threshold.
"""
import re
from dataclasses import dataclass
from pathlib import Path

from app.config import get_settings
from app.retrieval.embeddings import embed_query
from app.retrieval.vector_store import list_sources
from app.retrieval.vector_store import query as vs_query

CANDIDATES = 24
KEYWORD_WEIGHT = 0.04

# words that appear in many file names and say nothing about which file is meant
GENERIC_NAME_WORDS = {
    "agro", "advisories", "advisory", "farmers", "kharif", "rabi", "contingency",
    "plan", "district", "state", "india", "guide", "management", "scheme",
}
STOPWORDS = {
    "what", "when", "where", "which", "does", "have", "with", "from", "that",
    "this", "your", "about", "normal", "much", "many", "there", "their", "should",
}


@dataclass
class RetrievedChunk:
    text: str
    source: str
    page: int
    distance: float


def prepare_query(question: str) -> str:
    """Prepare and validate the query."""
    q = " ".join(question.split())
    if len(q) < 3:
        raise ValueError("Question is too short.")
    if len(q) > 1000:
        raise ValueError("Question is too long (max 1000 characters).")
    return q


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{4,}", text.lower()))


def detect_sources(question: str, sources: list[str]) -> list[str]:
    """Files whose name contains a distinctive word used in the question
    (e.g. 'Bagalkot' -> KA1-Bagalkot_31.1.2011.pdf)."""
    q = _words(question)
    hits = []
    for src in sources:
        name_words = {
            w for w in re.findall(r"[a-z]{4,}", Path(src).stem.lower())
            if w not in GENERIC_NAME_WORDS
        }
        if name_words & q:
            hits.append(src)
    return hits


def retrieve(question: str, top_k: int | None = None) -> list[RetrievedChunk]:
    """Return only chunks that pass the relevance threshold (may be empty)."""
    s = get_settings()
    k = top_k or s.top_k

    named = detect_sources(question, list_sources())
    where = {"source": {"$in": named}} if named else None

    res = vs_query(embed_query(question), max(CANDIDATES, k), where)
    if not res["documents"] or not res["documents"][0]:
        return []

    q_words = _words(question) - STOPWORDS
    scored = []
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        if dist > s.max_distance:
            continue
        overlap = len(q_words & _words(text))
        score = (1 - dist) + KEYWORD_WEIGHT * overlap
        scored.append((score, RetrievedChunk(text, meta["source"], meta["page"], dist)))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:k]]
