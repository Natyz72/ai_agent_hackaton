from typing import Any
from app.schemas.tools import SearchGuidanceInput
from app.tools.search_guidance import search_guidance


class FakeGuidanceRepo:
    def __init__(self):
        self.passages = [
            {
                "id": "SEC-01",
                "title": "Verify sender identity",
                "content": "Always verify the sender through a separate channel before taking action on urgent requests.",
                "excerpt": "Verify sender through a separate channel.",
            },
            {
                "id": "SEC-02",
                "title": "Be cautious with urgent requests",
                "content": "Urgency and pressure are common social engineering tactics.",
                "excerpt": "Urgency is a common red flag.",
            },
            {
                "id": "SEC-03",
                "title": "Inspect URLs carefully",
                "content": "Check URLs for misspellings, unusual domains, and user-info tricks.",
                "excerpt": "Inspect URLs for anomalies.",
            },
        ]

    def search_guidance(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        return [
            p for p in self.passages
            if q in p["title"].lower() or q in p["content"].lower()
        ]

    def get_guidance_by_id(self, gid: str) -> dict[str, Any] | None:
        for p in self.passages:
            if p["id"] == gid:
                return p
        return None


def test_search_guidance_query_match():
    repo = FakeGuidanceRepo()
    result = search_guidance(SearchGuidanceInput(query="sender"), repo=repo)
    assert len(result.guidance) == 1
    # ID must be the exact real DB ID, never invented
    assert result.guidance[0]["id"] == "SEC-01"
    assert "Verify sender" in result.guidance[0]["title"]
    assert len(result.findings) == 1
    assert result.findings[0].status == "detected"
    assert "SEC-01" in result.findings[0].evidence_ids


def test_search_guidance_no_match():
    repo = FakeGuidanceRepo()
    result = search_guidance(SearchGuidanceInput(query="cryptocurrency mining"), repo=repo)
    assert len(result.guidance) == 0
    assert len(result.findings) == 1
    assert result.findings[0].status == "not_detected"


def test_search_guidance_findings_context_fallback():
    repo = FakeGuidanceRepo()
    result = search_guidance(
        SearchGuidanceInput(
            query="",
            findings_context=[
                {"category": "social_engineering", "reason": "High urgency detected"}
            ],
        ),
        repo=repo,
    )
    assert len(result.guidance) >= 1
    assert any(g["id"] == "SEC-02" for g in result.guidance)
