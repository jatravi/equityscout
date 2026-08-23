from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps.api.src.services.parsers.html_parser import parse_html
from apps.api.src.services.parsers.pdf_parser import parse_pdf


@dataclass
class ParseResult:
    title: str | None
    plain_text: str
    metadata: dict[str, Any]


def _looks_like_pdf(content_bytes: bytes) -> bool:
    # PDF files start with magic bytes: %PDF
    return content_bytes[:4] == b"%PDF"


def parse_document(content_bytes: bytes, content_type: str | None = None) -> ParseResult:
    ct = (content_type or "").lower()

    # Decide by content-type first
    if "application/pdf" in ct:
        r = parse_pdf(content_bytes, content_type=content_type)
        return ParseResult(title=r.title, plain_text=r.plain_text, metadata=r.metadata)

    if "text/html" in ct or "application/xhtml+xml" in ct:
        r = parse_html(content_bytes, content_type=content_type)
        return ParseResult(title=r.title, plain_text=r.plain_text, metadata=r.metadata)

    # Fallback by file signature
    if _looks_like_pdf(content_bytes):
        r = parse_pdf(content_bytes, content_type=content_type)
        return ParseResult(title=r.title, plain_text=r.plain_text, metadata=r.metadata)

    # Last fallback: attempt html parse (works for many text-like pages)
    r = parse_html(content_bytes, content_type=content_type)
    r.metadata["warnings"] = list(r.metadata.get("warnings", [])) + ["fallback_html_parse_used"]
    return ParseResult(title=r.title, plain_text=r.plain_text, metadata=r.metadata)