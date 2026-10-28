"""Orchestrates the full RAG flow shown in the flowchart."""
from app.generation.llm import generate
from app.generation.prompt import build_prompt
from app.retrieval.retriever import prepare_query, retrieve

NO_EVIDENCE_MESSAGE = (
    "I could not find enough information in the knowledge base to answer this "
    "reliably. Could you add more detail (crop, growth stage, symptoms, region)?"
)


def answer_question(question: str) -> dict:
    query = prepare_query(question)          # Prepare and validate query
    chunks = retrieve(query)                 # Embed -> search ChromaDB -> retrieve chunks

    if not chunks:                           # Relevant information found? -> No
        return {"answer": NO_EVIDENCE_MESSAGE, "sources": [], "grounded": False}

    prompt = build_prompt(query, chunks)     # Yes: build prompt with retrieved context
    answer = generate(prompt)                # Send to Gemini -> context-grounded answer

    sources = [
        {"source": c.source, "page": c.page, "score": round(1 - c.distance, 3), "snippet": c.text[:200]}
        for c in chunks
    ]
    return {"answer": answer, "sources": sources, "grounded": True}
