"""Ingestion pipeline: load -> clean -> split -> embed -> store in ChromaDB.

Run:  python -m app.ingestion.indexing [--reset]
"""
import argparse
import json

from app.config import get_settings
from app.ingestion.document_loader import PageDoc, load_documents
from app.ingestion.text_cleaner import clean_text
from app.ingestion.text_splitter import split_documents
from app.retrieval.embeddings import embed_texts
from app.retrieval.vector_store import add_chunks, reset_collection

BATCH = 64


def run_indexing(reset: bool = False) -> int:
    s = get_settings()
    raw_dir = s.path(s.raw_data_dir)
    if reset:
        reset_collection()

    pages = load_documents(raw_dir)
    if not pages:
        raise SystemExit(f"No documents found in {raw_dir}. Add PDFs to data/raw/ first.")

    cleaned = [PageDoc(p.source, p.page, clean_text(p.text)) for p in pages]
    chunks = split_documents(cleaned, s.chunk_size, s.chunk_overlap)

    # Save processed chunks for inspection / debugging.
    out = s.path(s.processed_data_dir) / "chunks.json"
    out.write_text(
        json.dumps([c.__dict__ for c in chunks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for i in range(0, len(chunks), BATCH):
        batch = chunks[i : i + BATCH]
        texts = [c.text for c in batch]
        add_chunks(
            ids=[c.id for c in batch],
            documents=texts,
            embeddings=embed_texts(texts),
            metadatas=[{"source": c.source, "page": c.page} for c in batch],
        )
    return len(chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="drop and rebuild the collection")
    args = parser.parse_args()
    n = run_indexing(reset=args.reset)
    print(f"Indexed {n} chunks.")
