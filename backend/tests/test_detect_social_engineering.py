from app.tools.detect_social_engineering import detect_social_engineering
from app.schemas.tools import DetectSocialEngineeringInput


def test_se_urgency():
    msg = "URGENT: Your account will be suspended if you don't act now!"
    res = detect_social_engineering(DetectSocialEngineeringInput(message=msg))
    assert any(f.id == "SE-URGENCY" and f.status == "detected" for f in res.findings)
    assert res.tactics


def test_se_credential_request():
    msg = "Please send your password and OTP code immediately"
    res = detect_social_engineering(DetectSocialEngineeringInput(message=msg))
    assert any(f.id == "SE-CREDENTIAL_REQUEST" and f.status == "detected" for f in res.findings)


def test_se_payment():
    msg = "Send payment via gift card to complete this transaction"
    res = detect_social_engineering(DetectSocialEngineeringInput(message=msg))
    assert any(f.id == "SE-PAYMENT_REDIRECT" and f.status == "detected" for f in res.findings)


def test_se_clean():
    msg = "Meeting scheduled for tomorrow at 3pm"
    res = detect_social_engineering(DetectSocialEngineeringInput(message=msg))
    for f in res.findings:
        assert f.status == "not_detected"


def test_se_offsets():
    msg = "URGENT action required"
    res = detect_social_engineering(DetectSocialEngineeringInput(message=msg))
    for f in res.findings:
        for sp in f.source_evidence:
            assert msg[sp.start:sp.end] == sp.text
            assert 0 <= sp.start < sp.end <= len(msg)
