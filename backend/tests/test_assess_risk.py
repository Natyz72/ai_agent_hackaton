from app.schemas.common import Finding
from app.services.assess_risk import assess_risk


def test_assess_risk_low():
    findings = [
        Finding(
            id="IND-EMAIL",
            category="indicators",
            status="not_detected",
            reason="No emails found",
        )
    ]
    assessment = assess_risk(findings)
    assert assessment.level == "low"
    assert assessment.score < 30
    assert assessment.heuristic is True


def test_assess_risk_medium():
    findings = [
        Finding(
            id="SE-URGENCY",
            category="social_engineering",
            status="detected",
            reason="Urgency detected",
        )
    ]
    assessment = assess_risk(findings)
    # Urgency adds 20 points -> low (<30) or if another indicator added -> medium
    findings.append(
        Finding(
            id="IND-SENSITIVE",
            category="indicators",
            status="detected",
            reason="Sensitive terms",
        )
    )
    assessment = assess_risk(findings)
    assert assessment.level == "medium"
    assert 30 <= assessment.score < 60


def test_assess_risk_high():
    findings = [
        Finding(
            id="SE-CREDS",
            category="social_engineering",
            status="detected",
            reason="Credential request detected",
        ),
        Finding(
            id="SE-URGENCY",
            category="social_engineering",
            status="detected",
            reason="Urgent deadline detected",
        ),
    ]
    urls_analysis = [
        {
            "url": "hxxp[://]192[.]168[.]1[.]1/login",
            "is_ip": True,
            "has_user_info": False,
            "suspicious": True,
            "reasons": ["URL uses IP address"],
        }
    ]
    reputation_results = [
        {
            "hostname": "phishy.example",
            "status": "suspicious",
            "source": "synthetic_demo",
            "reason": "Flagged domain",
        }
    ]

    assessment = assess_risk(
        findings=findings,
        urls_analysis=urls_analysis,
        reputation_results=reputation_results,
    )
    assert assessment.level == "high"
    assert assessment.score >= 60
    assert len(assessment.breakdown) > 0


def test_assess_risk_unknown_domain_does_not_lower_score():
    findings = [
        Finding(
            id="SE-CREDS",
            category="social_engineering",
            status="detected",
            reason="Credential request",
        )
    ]
    reputation_results = [
        {
            "hostname": "unknown.example",
            "status": "unknown",
            "source": "database",
            "reason": "No data",
        }
    ]
    assessment = assess_risk(findings=findings, reputation_results=reputation_results)
    # Score should be at least the points from SE-CREDS (30)
    assert assessment.score >= 30
    assert any("unknown reputation" in n for n in assessment.notes)
