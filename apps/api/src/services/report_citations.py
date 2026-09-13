from __future__ import annotations

import re
from typing import Any

CIT_RE = re.compile(r"\[E\d+\]")

def normalize_locator(locator: str | None) -> str:
    if not locator:
        return ""
    return " ".join(locator.strip().split())

def build_evidence_ref_map(evidence_rows: list[dict[str, Any]]) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """
    Deterministically assign [E1], [E2], ... to unique evidence locators.
    Returns:
      locator_to_ref: {"<locator>": "[E1]"}
      ordered_refs: [{"ref":"[E1]","title":"...","url":"...","snippet":"...","locator":"..."}]
    """
    unique: dict[str, dict[str, Any]] = {}

    for ev in evidence_rows:
        locator = normalize_locator(ev.get("locator"))
        if not locator:
            continue
        if locator in unique:
            continue
        unique[locator] = {
            "title": ev.get("title") or ev.get("key") or "Evidence",
            "url": ev.get("canonical_url") or ev.get("url") or "",
            "snippet": ev.get("snippet") or "",
            "locator": locator,
        }

    # deterministic order: by locator text
    locators = sorted(unique.keys())
    locator_to_ref: dict[str, str] = {}
    ordered_refs: list[dict[str, Any]] = []

    for i, loc in enumerate(locators, start=1):
        ref = f"[E{i}]"
        locator_to_ref[loc] = ref
        meta = unique[loc]
        ordered_refs.append(
            {
                "ref": ref,
                "title": meta["title"],
                "url": meta["url"],
                "snippet": meta["snippet"],
                "locator": meta["locator"],
            }
        )

    return locator_to_ref, ordered_refs

def refs_for_claim(claim: dict[str, Any], locator_to_ref: dict[str, str]) -> list[str]:
    """
    Map claim supporting locators to [E#] refs.
    Accepts:
      claim["supportingLocators"] as list[str]
      claim["supporting_locators"] as list[str]
    """
    locs = claim.get("supportingLocators") or claim.get("supporting_locators") or []
    refs: list[str] = []
    seen = set()
    for loc in locs:
        key = normalize_locator(loc)
        ref = locator_to_ref.get(key)
        if ref and ref not in seen:
            refs.append(ref)
            seen.add(ref)
    return refs

def append_refs(text: str, refs: list[str]) -> str:
    text = (text or "").strip()
    if not text:
        return text
    if not refs:
        return text
    suffix = " " + " ".join(refs)
    if suffix.strip() in text:
        return text
    return f"{text}{suffix}"

def count_inline_citations(markdown: str) -> int:
    return len(CIT_RE.findall(markdown or ""))