from app.tools.inspect_indicators import inspect_indicators
from app.schemas.tools import InspectIndicatorsInput


def test_inspect_indicators_email_detected():
    msg = "Contact me at test@example.com for details"
    res = inspect_indicators(InspectIndicatorsInput(message=msg))
    assert any(f.id == "IND-EMAIL" and f.status == "detected" for f in res.findings)
    assert res.indicators


def test_inspect_indicators_no_email():
    msg = "Hello there, this is a normal message"
    res = inspect_indicators(InspectIndicatorsInput(message=msg))
    assert any(f.id == "IND-EMAIL" and f.status == "not_detected" for f in res.findings)


def test_inspect_indicators_urgent_creds():
    msg = "URGENT: Verify your password immediately"
    res = inspect_indicators(InspectIndicatorsInput(message=msg))
    assert any(f.id == "IND-SENSITIVE" and f.status == "detected" for f in res.findings)


def test_inspect_indicators_offsets_valid():
    msg = "Email: test@example.com now"
    res = inspect_indicators(InspectIndicatorsInput(message=msg))
    for f in res.findings:
        for sp in f.source_evidence:
            assert 0 <= sp.start < sp.end <= len(msg)
            assert msg[sp.start:sp.end] == sp.text
