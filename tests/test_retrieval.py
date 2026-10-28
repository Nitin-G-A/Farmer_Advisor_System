import pytest

from app.retrieval import retriever
from app.retrieval.retriever import detect_sources, prepare_query

SOURCES = [
    "KA1-Bagalkot_31.1.2011.pdf",
    "KA25-Bellary_04.10.2011.pdf",
    "ICAR-En-Kharif-Agro-Advisories-for-Farmers-2025.pdf",
    "PMKisanSamanNidhi.pdf",
]


def test_prepare_query_normalizes_whitespace():
    assert prepare_query("  how   to  water  tomato ") == "how to water tomato"


def test_prepare_query_rejects_short():
    with pytest.raises(ValueError):
        prepare_query("hi")


def test_detect_sources_finds_district():
    assert detect_sources("What is the normal annual rainfall in Bagalkot?", SOURCES) == [
        "KA1-Bagalkot_31.1.2011.pdf"
    ]


def test_detect_sources_none_for_generic_question():
    assert detect_sources("How do I control early blight?", SOURCES) == []


def _patch(monkeypatch, fake):
    monkeypatch.setattr(retriever, "embed_query", lambda q: [0.0])
    monkeypatch.setattr(retriever, "list_sources", lambda: SOURCES)
    monkeypatch.setattr(retriever, "vs_query", lambda emb, k, where=None: fake)


def test_retrieve_filters_by_distance(monkeypatch):
    fake = {
        "documents": [["close chunk", "far chunk"]],
        "metadatas": [[{"source": "a.pdf", "page": 1}, {"source": "b.pdf", "page": 2}]],
        "distances": [[0.2, 0.95]],
    }
    _patch(monkeypatch, fake)
    assert [c.text for c in retriever.retrieve("anything")] == ["close chunk"]


def test_retrieve_reranks_by_keyword(monkeypatch):
    fake = {
        "documents": [["unrelated text", "annual rainfall 585 mm"]],
        "metadatas": [[{"source": "a.pdf", "page": 1}, {"source": "b.pdf", "page": 2}]],
        "distances": [[0.40, 0.45]],
    }
    _patch(monkeypatch, fake)
    top = retriever.retrieve("annual rainfall")[0]
    assert top.text == "annual rainfall 585 mm"


def test_retrieve_returns_empty_when_nothing_relevant(monkeypatch):
    fake = {"documents": [["far"]], "metadatas": [[{"source": "a.pdf", "page": 1}]], "distances": [[0.99]]}
    _patch(monkeypatch, fake)
    assert retriever.retrieve("anything") == []
