# Farmer Advisor RAG

Retrieval-Augmented Generation component of the Farmer Advisor System. Farmers ask
agricultural questions; the system retrieves relevant passages from the knowledge base
(PDFs) and has Gemini answer **only** from that context, returning source references.

## Pipeline

```
Ingestion (offline):  PDFs -> load -> clean -> split into chunks -> embed -> ChromaDB
Query (online):       question -> FastAPI -> validate -> embed -> search ChromaDB
                      -> relevant? --no--> ask for clarification / insufficient evidence
                                   --yes-> build prompt -> Gemini -> answer + sources
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Edit `.env` and set `GEMINI_API_KEY`.

## Usage

1. Put your PDFs in `data/raw/` (e.g. `tomato_guide.pdf`, `soil_management.pdf`, `pest_management.pdf`).
2. Build the index:
   ```bash
   python -m app.ingestion.indexing --reset
   ```
3. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Open the chat UI at http://localhost:8000
5. Or call the API directly:
   ```bash
   curl -X POST localhost:8000/ask -H "Content-Type: application/json" \
     -d '{"question": "How do I control early blight in tomato?"}'
   ```
   Interactive docs: http://localhost:8000/docs

## Tests

```bash
pytest
```

## Tuning

- `MAX_DISTANCE` in `.env` is the relevance cutoff (cosine distance, lower = stricter). Tune it on real questions.
- `CHUNK_SIZE` / `CHUNK_OVERLAP` control chunking; inspect `data/processed/chunks.json` after indexing.
- The default embedding model is multilingual, so non-English questions can match English documents.
