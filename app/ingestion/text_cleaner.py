"""Clean text extracted from PDFs while keeping table rows on separate lines."""
import re
import unicodedata


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("­", "").replace("□", "")  # soft hyphens, missing-glyph boxes
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # re-join words hyphenated across lines

    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        # layout extraction pads table columns with runs of spaces -> mark cell borders
        line = re.sub(r" {2,}|\t+", " | ", line)
        lines.append(line)

    # Join wrapped prose lines (long line not ending a sentence) but keep short
    # lines such as table rows and headings on their own line.
    out: list[str] = []
    for line in lines:
        if (
            out
            and out[-1]
            and line
            and len(out[-1]) > 70
            and out[-1][-1] not in ".:;?!|"
            and "|" not in line
        ):
            out[-1] = out[-1] + " " + line
        else:
            out.append(line)

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
