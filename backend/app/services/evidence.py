from typing import Any
from app.schemas.common import EvidenceSpan, Finding


def is_valid_span(span: EvidenceSpan | dict[str, Any], message: str) -> bool:
    if isinstance(span, dict):
        start = span.get("start", -1)
        end = span.get("end", -1)
        text = span.get("text", "")
    else:
        start = span.start
        end = span.end
        text = span.text

    if not isinstance(start, int) or not isinstance(end, int):
        return False
    if start < 0 or end > len(message) or start >= end:
        return False
    return message[start:end] == text


def extract_span(message: str, start: int, end: int) -> EvidenceSpan | None:
    if 0 <= start < end <= len(message):
        return EvidenceSpan(start=start, end=end, text=message[start:end])
    return None


def build_highlights(findings: list[Finding | dict[str, Any]], message: str) -> list[dict[str, Any]]:
    highlights: list[dict[str, Any]] = []
    seen = set()

    for f in findings:
        spans = f.source_evidence if isinstance(f, Finding) else f.get("source_evidence", [])
        f_id = f.id if isinstance(f, Finding) else f.get("id", "finding")
        category = f.category if isinstance(f, Finding) else f.get("category", "general")

        for s in spans:
            if not is_valid_span(s, message):
                continue
            start = s.start if isinstance(s, EvidenceSpan) else s["start"]
            end = s.end if isinstance(s, EvidenceSpan) else s["end"]
            text = s.text if isinstance(s, EvidenceSpan) else s["text"]

            key = (start, end)
            if key not in seen:
                seen.add(key)
                highlights.append({
                    "start": start,
                    "end": end,
                    "text": text,
                    "finding_id": f_id,
                    "category": category,
                })

    highlights.sort(key=lambda h: h["start"])
    return highlights
