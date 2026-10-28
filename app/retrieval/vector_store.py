"""ChromaDB persistence layer."""
from app.config import BASE_DIR, get_settings


def _client():
    import chromadb  # lazy import

    return chromadb.PersistentClient(path=str(BASE_DIR / get_settings().chroma_dir))


def get_collection():
    return _client().get_or_create_collection(
        name=get_settings().collection_name, metadata={"hnsw:space": "cosine"}
    )


def reset_collection() -> None:
    try:
        _client().delete_collection(get_settings().collection_name)
    except Exception:
        pass


def add_chunks(ids, documents, embeddings, metadatas) -> None:
    get_collection().upsert(
        ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
    )


def list_sources() -> list[str]:
    metas = get_collection().get(include=["metadatas"])["metadatas"] or []
    return sorted({m["source"] for m in metas})


def query(embedding: list[float], top_k: int, where: dict | None = None) -> dict:
    kwargs = {"where": where} if where else {}
    return get_collection().query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
        **kwargs,
    )
