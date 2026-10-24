from app.tools.analyze_url_structure import analyze_url_structure
from app.schemas.tools import AnalyzeURLStructureInput


def test_url_parsing_basic():
    msg = "Click https://example.com/login"
    res = analyze_url_structure(AnalyzeURLStructureInput(message=msg))
    assert res.urls
    assert res.findings[0].status == "detected"


def test_user_info_trick():
    msg = "Go to https://trusted.example@attacker.example/phish"
    res = analyze_url_structure(AnalyzeURLStructureInput(message=msg))
    assert res.analysis
    assert res.analysis[0]["has_user_info"] is True
    assert res.analysis[0]["normalized_host"] == "attacker.example"


def test_ip_url():
    msg = "Visit http://192.168.1.1/login"
    res = analyze_url_structure(AnalyzeURLStructureInput(message=msg))
    assert res.analysis[0]["is_ip"] is True


def test_misleading_subdomain():
    msg = "https://trusted.example.attacker.example/page"
    res = analyze_url_structure(AnalyzeURLStructureInput(message=msg))
    assert res.analysis[0]["normalized_host"] == "trusted.example.attacker.example"


def test_no_urls():
    msg = "Just a message with no links"
    res = analyze_url_structure(AnalyzeURLStructureInput(message=msg))
    assert res.findings[0].status == "not_detected"
    assert res.urls == []


def test_offsets_valid():
    msg = "See http://bad.example.com/path now"
    res = analyze_url_structure(AnalyzeURLStructureInput(message=msg))
    for f in res.findings:
        for sp in f.source_evidence:
            assert 0 <= sp.start < sp.end <= len(msg)
            assert msg[sp.start:sp.end] == sp.text
