from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import Any

from pypdf import PdfReader


@dataclass
class ParseResult:
    title: str | None
    plain_text: str
    metadata: dict[str, Any]


def _clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def parse_pdf(content_bytes: bytes, content_type: str | None = None) -> ParseResult:
    warnings: list[str] = []
    pages_text: list[str] = []

    try:
        reader = PdfReader(io.BytesIO(content_bytes))
    except Exception as ex:
        return ParseResult(
            title=None,
            plain_text="",
            metadata={
                "lang": None,
                "length": 0,
                "parser_used": "pdf_parser_v1",
                "warnings": [f"pdf_open_failed:{type(ex).__name__}"],
                "content_type": content_type,
                "page_count": 0,
            },
        )

    title = None
    try:
        if reader.metadata and getattr(reader.metadata, "title", None):
            title = _clean_whitespace(reader.metadata.title)
    except Exception:
        warnings.append("pdf_metadata_title_read_failed")

    for i, page in enumerate(reader.pages):
        try:
            txt = page.extract_text() or ""
            txt = _clean_whitespace(txt)
            if txt:
                pages_text.append(txt)
            else:
                warnings.append(f"empty_text_page_{i+1}")
        except Exception:
            warnings.append(f"page_extract_failed_{i+1}")

    plain_text = _clean_whitespace(" ".join(pages_text))

    metadata = {
        "lang": None,  # PDF language detection skipped for v1
        "length": len(plain_text),
        "parser_used": "pdf_parser_v1",
        "warnings": warnings,
        "content_type": content_type,
        "page_count": len(reader.pages),
    }

    return ParseResult(title=title, plain_text=plain_text, metadata=metadata)