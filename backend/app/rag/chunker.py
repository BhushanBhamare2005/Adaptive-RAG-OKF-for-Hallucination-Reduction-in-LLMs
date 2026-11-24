from app.rag.document_processor import clean_text


def chunk_sections(
    sections: list[tuple[str, int | None, str | None]],
    chunk_size: int = 700,
    overlap: int = 100,
) -> list[dict]:
    chunks: list[dict] = []
    for text, page_number, section_title in sections:
        words = clean_text(text).split()
        if not words:
            continue
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            chunks.append({
                "text": chunk_text,
                "page_number": page_number,
                "section_title": section_title,
                "token_count": len(chunk_text.split()),
            })
            if end >= len(words):
                break
            start = max(end - overlap, start + 1)
    return chunks
