from app.schemas.common import Finding, EvidenceSpan, GuidanceRef
from app.services.validate_evidence import validate_evidence


class FakeRepo:
    def get_guidance_by_id(self, gid: str):
        if gid in ("SEC-01", "SEC-02", "SEC-03"):
            return {"id": gid, "title": f"Title {gid}", "content": "Content"}
        return None


def test_validate_evidence_valid_span():
    message = "Your account is suspended. Click here to verify."
    span = EvidenceSpan(start=0, end=26, text="Your account is suspended.")
    finding = Finding(
        id="SE-URGENCY",
        category="social_engineering",
        status="detected",
        reason="Suspension claim",
        source_evidence=[span],
    )

    validated, warnings = validate_evidence(message, [finding])
    assert len(warnings) == 0
    assert len(validated[0].source_evidence) == 1
    assert validated[0].source_evidence[0].text == "Your account is suspended."


def test_validate_evidence_out_of_bounds_span():
    message = "Short text"
    # Span exceeds message length
    span = EvidenceSpan(start=0, end=50, text="Out of bounds span text")
    finding = Finding(
        id="SE-URGENCY",
        category="social_engineering",
        status="detected",
        reason="Invalid span",
        source_evidence=[span],
    )

    validated, warnings = validate_evidence(message, [finding])
    assert len(warnings) > 0
    assert len(validated[0].source_evidence) == 0


def test_validate_evidence_text_mismatch_span():
    message = "Hello world"
    span = EvidenceSpan(start=0, end=5, text="Wrong")
    finding = Finding(
        id="SE-URGENCY",
        category="social_engineering",
        status="detected",
        reason="Mismatch span",
        source_evidence=[span],
    )

    validated, warnings = validate_evidence(message, [finding])
    assert len(warnings) > 0
    assert len(validated[0].source_evidence) == 0


def test_validate_evidence_rejects_invented_guidance_id():
    repo = FakeRepo()
    message = "Suspicious message"
    finding = Finding(
        id="GUID-RETRIEVAL",
        category="guidance",
        status="detected",
        reason="Guidance retrieval",
        evidence_ids=["SEC-01", "FAKE-INVENTED-99"],
    )

    validated, warnings = validate_evidence(message, [finding], repo=repo)
    # The fake ID should be rejected
    assert validated[0].evidence_ids == ["SEC-01"]
    assert any("FAKE-INVENTED-99" in w for w in warnings)


def test_validate_evidence_invalid_status_fallback():
    message = "Test message"
    finding = Finding(
        id="IND-1",
        category="indicators",
        status="bogus_status",
        reason="Testing status fallback",
    )

    validated, warnings = validate_evidence(message, [finding])
    assert validated[0].status == "not_assessable"
    assert len(warnings) > 0
