from app.ingestion.text_cleaner import clean_text
from app.ingestion.text_splitter import split_text


def test_clean_text_joins_hyphenated_and_lines():
    raw = "Tomato blight is a fun-\ngal disease.\nIt spreads fast.\n\n\n\nNext."
    out = clean_text(raw)
    assert "fungal" in out
    assert "\n\n\n" not in out


def test_split_text_respects_size_and_overlap():
    text = ("Tomato plants need well drained soil. " * 80).strip()
    chunks = split_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 300 for c in chunks)


def test_split_text_rejects_bad_overlap():
    import pytest

    with pytest.raises(ValueError):
        split_text("abc", chunk_size=10, overlap=10)
