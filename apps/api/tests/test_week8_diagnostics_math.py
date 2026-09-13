from apps.api.src.services.diagnostics_service import safe_rate, build_diagnostics_payload, StageMetrics


def test_safe_rate_bounds_and_zero_division():
    assert safe_rate(0, 0) == 0.0
    assert safe_rate(5, 10) == 0.5
    assert safe_rate(-1, 10) == 0.0
    assert safe_rate(11, 10) == 1.0


def test_build_payload_fields_present_and_valid():
    payload = build_diagnostics_payload(
        run_id="r1",
        source_total=10,
        source_success=8,
        docs_total=20,
        docs_parsed=15,
        evidence_count=30,
        claims_count=12,
        citation_count=9,
        report_validation_status="VALID",
        validation_error_count=1,
        token_input=1200,
        token_output=800,
        estimated_cost=0.0345,
        stage_metrics=StageMetrics(10, 20, 30, 40, 50),
    )

    assert payload["runId"] == "r1"
    assert payload["sourceSuccessRate"] == 0.8
    assert payload["parserFailureRate"] == 0.25
    assert 0.0 <= payload["sourceSuccessRate"] <= 1.0
    assert 0.0 <= payload["parserFailureRate"] <= 1.0
    assert payload["reportValidationStatus"] == "VALID"
    