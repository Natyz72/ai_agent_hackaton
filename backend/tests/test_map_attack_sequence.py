from app.schemas.tools import MapAttackSequenceInput
from app.tools.map_attack_sequence import map_attack_sequence


def test_map_attack_sequence_with_findings():
    message = "Your account is locked. Please login at hxxp://evil.example to confirm payment."
    findings = [
        {
            "id": "IND-EMAIL",
            "category": "indicators",
            "status": "detected",
            "reason": "Indicator detected",
            "source_evidence": [],
        },
        {
            "id": "SE-URGENCY",
            "category": "social_engineering",
            "status": "detected",
            "reason": "Account locked urgency",
            "source_evidence": [{"start": 0, "end": 22, "text": "Your account is locked"}],
        },
        {
            "id": "URL-ANOMALY",
            "category": "url_structure",
            "status": "detected",
            "reason": "Suspicious URL",
            "source_evidence": [],
        },
        {
            "id": "SE-PAYMENT",
            "category": "social_engineering",
            "status": "detected",
            "reason": "Payment action",
            "source_evidence": [],
        },
    ]

    result = map_attack_sequence(MapAttackSequenceInput(message=message, findings=findings))
    assert len(result.steps) >= 3
    # Verify sequence step numbers are ordered
    step_nums = [s["step"] for s in result.steps]
    assert step_nums == list(range(1, len(result.steps) + 1))
    # Verify steps describe attacker actions without implying recipient compliance
    for step in result.steps:
        assert "Attacker" in step["description"]

    assert len(result.findings) == 1
    assert result.findings[0].status == "detected"


def test_map_attack_sequence_empty_message():
    result = map_attack_sequence(MapAttackSequenceInput(message="", findings=[]))
    assert len(result.steps) == 0
    assert result.findings[0].status == "not_detected"
