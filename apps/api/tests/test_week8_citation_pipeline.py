from apps.api.src.services.report_citations import (
    build_evidence_ref_map,
    refs_for_claim,
    append_refs,
    count_inline_citations,
)

def test_build_evidence_ref_map_deterministic():
    evidence = [
        {"locator": "p2:para1", "title": "Doc B", "url": "u2", "snippet": "s2"},
        {"locator": "p1:para5", "title": "Doc A", "url": "u1", "snippet": "s1"},
        {"locator": "p1:para5", "title": "Doc A dup", "url": "u1x", "snippet": "s1x"},
    ]
    locator_to_ref, ordered = build_evidence_ref_map(evidence)
    assert locator_to_ref["p1:para5"] == "[E1]"
    assert locator_to_ref["p2:para1"] == "[E2]"
    assert len(ordered) == 2

def test_refs_for_claim_and_append():
    locator_to_ref = {"p1:para5": "[E1]", "p2:para1": "[E2]"}
    claim = {"claimText": "Revenue improved YoY", "supportingLocators": ["p2:para1", "p1:para5"]}
    refs = refs_for_claim(claim, locator_to_ref)
    assert refs == ["[E2]", "[E1]"]  # preserves claim locator order

    out = append_refs(claim["claimText"], refs)
    assert out.endswith("[E2] [E1]")

def test_count_inline_citations():
    md = "- A [E1]\n- B [E2] [E3]\n- C"
    assert count_inline_citations(md) == 3