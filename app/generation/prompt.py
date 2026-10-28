"""Build the context-grounded prompt."""
from app.retrieval.retriever import RetrievedChunk

SYSTEM_INSTRUCTIONS = """You are an agricultural advisor helping farmers.
Answer ONLY using the context below. If the context does not contain enough
information, say so clearly instead of guessing. Use simple, practical language.
Reply in the same language as the farmer's question. Mention the source
numbers like [1], [2] that support your answer. Do not invent dosages,
chemical names or quantities that are not in the context."""


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n".join(
        f"[{i}] (source: {c.source}, page {c.page})\n{c.text}"
        for i, c in enumerate(chunks, start=1)
    )
    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"### Context\n{context}\n\n"
        f"### Farmer's question\n{question}\n\n"
        f"### Answer"
    )
