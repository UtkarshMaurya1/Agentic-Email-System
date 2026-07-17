import re
from dataclasses import dataclass

import pypdf

DAY_HEADER_PATTERN = re.compile(r"^\s*(Day\s+\d+.*|Section\s*[:\-].*)\s*$", re.IGNORECASE)
FALLBACK_CHUNK_SIZE = 800   # chars
FALLBACK_OVERLAP = 100


@dataclass
class Chunk:
    text: str
    section_label: str
    chunk_index: int


def extract_text(pdf_path: str) -> str:
    reader = pypdf.PdfReader(pdf_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def chunk_by_sections(full_text: str) -> list[Chunk]:
    """Split on lines matching DAY_HEADER_PATTERN. Returns [] if none found."""
    lines = full_text.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_label = None
    current_lines: list[str] = []

    for line in lines:
        if DAY_HEADER_PATTERN.match(line):
            if current_label is not None:
                sections.append((current_label, current_lines))
            current_label = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_label is not None:
        sections.append((current_label, current_lines))

    return [
        Chunk(text="\n".join(body).strip(), section_label=label, chunk_index=i)
        for i, (label, body) in enumerate(sections)
        if "\n".join(body).strip()
    ]


def chunk_fixed_size(full_text: str) -> list[Chunk]:
    """Fallback: sliding-window chunking with overlap."""
    chunks = []
    start = 0
    idx = 0
    text = full_text.strip()
    while start < len(text):
        end = start + FALLBACK_CHUNK_SIZE
        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(text=piece, section_label="", chunk_index=idx))
            idx += 1
        start += FALLBACK_CHUNK_SIZE - FALLBACK_OVERLAP
    return chunks


def chunk_pdf(pdf_path: str) -> list[Chunk]:
    full_text = extract_text(pdf_path)
    section_chunks = chunk_by_sections(full_text)
    if section_chunks:
        return section_chunks
    return chunk_fixed_size(full_text)