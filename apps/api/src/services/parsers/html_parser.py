from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup


@dataclass
class ParseResult:
    title: str | None
    plain_text: str
    metadata: dict[str, Any]


def _clean_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def _extract_main_html_text(soup: BeautifulSoup) -> tuple[str, list[str]]:
    warnings: list[str] = []

    # Remove noisy elements
    for tag in soup(["script", "style", "noscript", "svg", "canvas", "iframe", "footer", "nav", "aside"]):
        tag.decompose()

    # readability-style heuristic: prefer article/main/body in that order
    container = soup.find("article") or soup.find("main") or soup.body or soup
    text = container.get_text(separator=" ", strip=True) if container else ""

    if not text:
        warnings.append("empty_text_after_extraction")

    return _clean_whitespace(text), warnings


def parse_html(content_bytes: bytes, content_type: str | None = None) -> ParseResult:
    # Basic charset handling
    # (BeautifulSoup can often infer; this keeps it simple/robust)
    soup = BeautifulSoup(content_bytes, "html.parser")

    title_tag = soup.find("title")
    title = _clean_whitespace(title_tag.get_text()) if title_tag and title_tag.get_text() else None

    plain_text, warnings = _extract_main_html_text(soup)

    # naive language hint from html lang attr
    html_tag = soup.find("html")
    lang = html_tag.get("lang") if html_tag else None
    if isinstance(lang, str):
        lang = lang.strip() or None

    metadata = {
        "lang": lang,
        "length": len(plain_text),
        "parser_used": "html_parser_v1",
        "warnings": warnings,
        "content_type": content_type,
    }

    return ParseResult(title=title, plain_text=plain_text, metadata=metadata)