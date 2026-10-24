from typing import Any
from app.schemas.tools import (
    InspectIndicatorsInput,
    AnalyzeURLStructureInput,
    DetectSocialEngineeringInput,
    CheckDomainReputationInput,
    SearchGuidanceInput,
    MapAttackSequenceInput,
)
from app.tools.inspect_indicators import inspect_indicators
from app.tools.analyze_url_structure import analyze_url_structure
from app.tools.detect_social_engineering import detect_social_engineering
from app.tools.check_domain_reputation import check_domain_reputation
from app.tools.search_guidance import search_guidance
from app.tools.map_attack_sequence import map_attack_sequence
from app.db.repositories import Repository


# Strict registry: ONLY these 6 tools are declared.
# create_incident is intentionally NOT present in this registry.
TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "inspect_indicators",
        "description": "Inspect message for email addresses, phone numbers, and sensitive keywords with offsets.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "message": {"type": "STRING", "description": "The exact raw message text to inspect."},
            },
            "required": ["message"],
        },
    },
    {
        "name": "analyze_url_structure",
        "description": "Deterministically parse URLs for anomalies (IP addresses, user-info spoofs, misleading subdomains). Never visits the URL.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "message": {"type": "STRING", "description": "The message text containing URLs."},
            },
            "required": ["message"],
        },
    },
    {
        "name": "detect_social_engineering",
        "description": "Analyze message text for urgency, authority claims, credential requests, and payment lures.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "message": {"type": "STRING", "description": "The message text to analyze."},
            },
            "required": ["message"],
        },
    },
    {
        "name": "check_domain_reputation",
        "description": "Check hostnames against the internal synthetic domain reputation database. Unknown status means unknown.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "hostnames": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "List of normalized hostnames to look up.",
                },
            },
            "required": ["hostnames"],
        },
    },
    {
        "name": "search_guidance",
        "description": "Search verified security handbook guidance passages in the database. Returns real passage IDs only.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING", "description": "Search query terms (e.g. 'urgency', 'credentials')."},
            },
            "required": ["query"],
        },
    },
    {
        "name": "map_attack_sequence",
        "description": "Map attacker tactic phases based on identified evidence without asserting recipient compliance.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "message": {"type": "STRING", "description": "The message text."},
                "findings": {
                    "type": "ARRAY",
                    "items": {"type": "OBJECT"},
                    "description": "List of findings identified so far.",
                },
            },
            "required": ["message", "findings"],
        },
    },
]

ALLOWED_TOOL_NAMES = {t["name"] for t in TOOL_DEFINITIONS}


def execute_tool(
    name: str,
    arguments: dict[str, Any],
    repo: Repository | None = None,
) -> Any:
    """
    Executes an allowed tool with strict input validation.
    Disallows any tool not explicitly listed in ALLOWED_TOOL_NAMES (e.g. create_incident).
    """
    if name not in ALLOWED_TOOL_NAMES:
        raise ValueError(f"Unauthorized or unknown tool: '{name}'. Tool execution rejected.")

    if name == "inspect_indicators":
        inp = InspectIndicatorsInput(**arguments)
        return inspect_indicators(inp)
    elif name == "analyze_url_structure":
        inp = AnalyzeURLStructureInput(**arguments)
        return analyze_url_structure(inp)
    elif name == "detect_social_engineering":
        inp = DetectSocialEngineeringInput(**arguments)
        return detect_social_engineering(inp)
    elif name == "check_domain_reputation":
        inp = CheckDomainReputationInput(**arguments)
        return check_domain_reputation(inp, repo=repo)
    elif name == "search_guidance":
        inp = SearchGuidanceInput(**arguments)
        return search_guidance(inp, repo=repo)
    elif name == "map_attack_sequence":
        inp = MapAttackSequenceInput(**arguments)
        return map_attack_sequence(inp)
    else:
        raise ValueError(f"No execution handler for tool '{name}'")
