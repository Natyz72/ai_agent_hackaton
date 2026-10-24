from typing import Any
from app.schemas.tools import CheckDomainReputationInput
from app.tools.check_domain_reputation import check_domain_reputation, _normalize_hostname


class FakeRepo:
    def __init__(self):
        self.reputation_db = {
            "suspicious.example": {
                "hostname": "suspicious.example",
                "status": "suspicious",
                "source": "synthetic_demo",
                "reason": "Synthetic demo entry - flagged pattern",
            },
            "phishy.example": {
                "hostname": "phishy.example",
                "status": "suspicious",
                "source": "synthetic_demo",
                "reason": "Synthetic demo entry - suspicious indicators",
            },
            "trusted.example": {
                "hostname": "trusted.example",
                "status": "known_trusted",
                "source": "synthetic_demo",
                "reason": "Synthetic trusted domain",
            },
        }
        self.trusted_domains = [
            {"domain": "trusted.example", "reason": "Trusted domain"},
            {"domain": "company.example", "reason": "Internal domain"},
        ]

    def get_domain_reputation(self, hostname: str) -> dict[str, Any] | None:
        return self.reputation_db.get(hostname)

    def get_trusted_domains(self) -> list[dict[str, Any]]:
        return self.trusted_domains


def test_normalize_hostname():
    assert _normalize_hostname("HTTPS://Example.COM/path/page") == "example.com"
    assert _normalize_hostname("admin:secret@malicious.com:8080") == "malicious.com"
    assert _normalize_hostname("sub.domain.org.") == "sub.domain.org"


def test_check_domain_reputation_known_trusted():
    repo = FakeRepo()
    result = check_domain_reputation(
        CheckDomainReputationInput(hostnames=["trusted.example"]),
        repo=repo,
    )
    assert len(result.results) == 1
    assert result.results[0]["status"] == "known_trusted"
    assert result.results[0]["hostname"] == "trusted.example"

    # Finding should be not_detected for threats
    assert len(result.findings) == 1
    assert result.findings[0].status == "not_detected"


def test_check_domain_reputation_suspicious():
    repo = FakeRepo()
    result = check_domain_reputation(
        CheckDomainReputationInput(hostnames=["PHISHY.EXAMPLE"]),
        repo=repo,
    )
    assert len(result.results) == 1
    assert result.results[0]["status"] == "suspicious"
    assert result.results[0]["hostname"] == "phishy.example"

    assert len(result.findings) == 1
    assert result.findings[0].status == "detected"


def test_check_domain_reputation_unknown():
    repo = FakeRepo()
    result = check_domain_reputation(
        CheckDomainReputationInput(hostnames=["unknown-domain-never-seen.com"]),
        repo=repo,
    )
    assert len(result.results) == 1
    # Unknown must NOT be classified as safe or suspicious
    assert result.results[0]["status"] == "unknown"
    assert result.findings[0].status == "not_assessable"


def test_check_domain_reputation_empty():
    repo = FakeRepo()
    result = check_domain_reputation(
        CheckDomainReputationInput(hostnames=[]),
        repo=repo,
    )
    assert len(result.results) == 0
    assert len(result.findings) == 0
