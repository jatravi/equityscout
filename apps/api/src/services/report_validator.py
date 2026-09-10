from __future__ import annotations

import re

CITATION_RE = re.compile(r"\[E\d+\]")

KEY_SECTIONS = {
    "## Business Model & Segment Direction",
    "## Financial Trend Commentary",
    "## Promoter & Governance Observations",
    "### Supporting points",
}

def validate_report_citations(markdown: str) -> dict:
    """
    Fail if key claim bullets in key sections are uncited.
    """
    lines = markdown.splitlines()
    current_section = ""
    errors: list[dict] = []

    for idx, line in enumerate(lines):
        striped = line.strip()
        if striped.startswith("## ") or striped.startswith("### "):
            current_section = striped
            continue

        if current_section in KEY_SECTIONS and striped.startswith("- "):
            text = striped[2:].strip()
            if not text:
                continue
            if "Limited claim coverage available" in text:
                continue
            if "No supporting points available" in text:
                continue
            if not CITATION_RE.search(text):
                errors.append(
                    {
                        "section": current_section,
                        "lineIndex": idx,
                        "message": "Key claim is missing citation.",
                        "claimText": text,
                    }
                )

    return {
        "isValid": len(errors) == 0,
        "uncitedClaimCount": len(errors),
        "errors": errors,
    }