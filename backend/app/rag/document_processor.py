import csv
import hashlib
import re
from io import BytesIO, StringIO
from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_text(filename: str, mime_type: str, data: bytes) -> list[tuple[str, int | None, str | None]]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf" or mime_type == "application/pdf":
        reader = PdfReader(BytesIO(data))
        return [(clean_text(page.extract_text() or ""), index, None) for index, page in enumerate(reader.pages, start=1) if clean_text(page.extract_text() or "")]
    if suffix == ".docx" or mime_type in {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}:
        document = DocxDocument(BytesIO(data))
        sections: list[tuple[str, int | None, str | None]] = []
        for paragraph in document.paragraphs:
            text = clean_text(paragraph.text)
            if text:
                sections.append((text, None, paragraph.style.name if paragraph.style else None))
        for table_index, table in enumerate(document.tables, start=1):
            for row_index, row in enumerate(table.rows, start=1):
                values = [clean_text(cell.text) for cell in row.cells]
                text = " | ".join(value for value in values if value)
                if text:
                    sections.append((text, None, f"Table {table_index}, Row {row_index}"))
        return sections
    if suffix == ".csv" or mime_type in {"text/csv", "application/csv"}:
        text = data.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(StringIO(text))
        sections = []
        for row_index, row in enumerate(reader, start=1):
            text = " | ".join(f"{key}: {value}" for key, value in row.items() if value)
            if text:
                sections.append((text, None, f"CSV row {row_index}"))
        return sections
    if suffix in {".txt", ".md"} or mime_type.startswith("text/"):
        return [(clean_text(data.decode("utf-8-sig", errors="replace")), None, None)]
    raise ValueError(f"Unsupported file type: {filename}")
