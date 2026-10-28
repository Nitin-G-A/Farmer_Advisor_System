"""Load raw agricultural documents (PDF / TXT) into page-level records."""
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class PageDoc:
    source: str  # file name, e.g. tomato_guide.pdf
    page: int  # 1-based page number
    text: str


def _extract(page) -> str:
    # layout mode keeps table columns/rows apart; fall back if unsupported
    try:
        return page.extract_text(extraction_mode="layout") or ""
    except Exception:
        return page.extract_text() or ""


def load_pdf(path: Path) -> list[PageDoc]:
    reader = PdfReader(str(path))
    return [
        PageDoc(source=path.name, page=i, text=_extract(page))
        for i, page in enumerate(reader.pages, start=1)
    ]


def load_txt(path: Path) -> list[PageDoc]:
    return [PageDoc(source=path.name, page=1, text=path.read_text(encoding="utf-8"))]


def load_documents(raw_dir: Path) -> list[PageDoc]:
    """Load every supported file in raw_dir."""
    docs: list[PageDoc] = []
    for path in sorted(raw_dir.iterdir()):
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            docs.extend(load_pdf(path))
        elif suffix in {".txt", ".md"}:
            docs.extend(load_txt(path))
    return docs
