import json
from typing import Any
import uuid

from app.config import settings
from app.llm.base import LLMClient
from app.agent.prompts import SYSTEM_INVESTIGATION_PROMPT
from app.agent.registry import TOOL_DEFINITIONS, ALLOWED_TOOL_NAMES, execute_tool
from app.db.repositories import Repository
from app.services.activity_log import record_activity
from app.services.validate_evidence import validate_evidence
from app.services.assess_risk import assess_risk
from app.services.evidence import build_highlights
from app.services.guidance_draft import generate_guidance_draft
from app.schemas.common import (
    ActivityEvent,
    Finding,
    URLAnalysis,
    ReputationResult,
    GuidanceRef,
    AttackStep,
    RiskAssessment,
)


async def run_investigation_loop(
    message: str,
    llm: LLMClient,
    repo: Repository | None = None,
) -> dict[str, Any]:
    """
    Bounded agent orchestration loop.
    Enforces tool call caps, injection boundaries, truthful activity logging,
    and Python-controlled evidence validation and risk assessment.
    """
    if repo is None:
        repo = Repository()

    activity_log: list[ActivityEvent] = []
    findings_map: dict[str, Finding] = {}
    urls_analysis: list[URLAnalysis] = []
    reputation_results: list[ReputationResult] = []
    guidance_refs: list[GuidanceRef] = []
    attack_steps: list[AttackStep] = []
    seen_tool_calls: set[str] = set()

    activity_log.append(
        record_activity("investigation_started", "success", {"message_length": len(message)})
    )

    conversation_messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": f"Investigate this suspicious message:\n\n```\n{message}\n```",
        }
    ]

    total_tool_calls = 0
    clarification_questions: list[str] = []
    max_calls = settings.max_tool_calls

    while total_tool_calls < max_calls:
        try:
            response = await llm.generate_response(
                messages=conversation_messages,
                tools=TOOL_DEFINITIONS,
                system_instruction=SYSTEM_INVESTIGATION_PROMPT,
            )
        except Exception as e:
            activity_log.append(
                record_activity("llm_call", "failed", {"error": str(e)})
            )
            break

        if response.clarification_questions:
            clarification_questions.extend(response.clarification_questions)

        if not response.tool_calls:
            # Model has completed tool calling
            activity_log.append(
                record_activity("llm_call", "completed", {"summary": response.content})
            )
            break

        executed_any = False
        for tc in response.tool_calls:
            if total_tool_calls >= max_calls:
                break

            # Reject unauthorized tools
            if tc.name not in ALLOWED_TOOL_NAMES:
                activity_log.append(
                    record_activity(
                        "tool_execution",
                        "rejected",
                        {"tool": tc.name, "reason": "Unauthorized tool"},
                    )
                )
                continue

            # Prevent duplicate identical calls
            call_signature = f"{tc.name}:{json.dumps(tc.arguments, sort_keys=True)}"
            if call_signature in seen_tool_calls:
                activity_log.append(
                    record_activity(
                        "tool_execution",
                        "skipped_duplicate",
                        {"tool": tc.name},
                    )
                )
                continue

            seen_tool_calls.add(call_signature)
            total_tool_calls += 1
            executed_any = True

            # If map_attack_sequence needs current findings, pass them
            args = dict(tc.arguments)
            if tc.name == "map_attack_sequence" and "findings" not in args:
                args["findings"] = [f.model_dump() for f in findings_map.values()]

            try:
                result = execute_tool(tc.name, args, repo=repo)
                activity_log.append(
                    record_activity(
                        "tool_execution",
                        "success",
                        {"tool": tc.name, "findings_count": len(getattr(result, "findings", []))},
                    )
                )

                # Process tool output into aggregated state
                if hasattr(result, "findings"):
                    for f in result.findings:
                        findings_map[f.id] = f

                if tc.name == "analyze_url_structure":
                    for a in getattr(result, "analysis", []):
                        urls_analysis.append(URLAnalysis(**a))

                elif tc.name == "check_domain_reputation":
                    for r in getattr(result, "results", []):
                        reputation_results.append(ReputationResult(**r))

                elif tc.name == "search_guidance":
                    for g in getattr(result, "guidance", []):
                        guidance_refs.append(GuidanceRef(**g))

                elif tc.name == "map_attack_sequence":
                    for s in getattr(result, "steps", []):
                        attack_steps.append(AttackStep(**s))

                # Add result to conversation messages for next round
                serialized_result = (
                    result.model_dump() if hasattr(result, "model_dump") else str(result)
                )
                conversation_messages.append({
                    "role": "model",
                    "tool_name": tc.name,
                    "tool_response": serialized_result,
                })

            except Exception as e:
                activity_log.append(
                    record_activity(
                        "tool_execution",
                        "failed",
                        {"tool": tc.name, "error": str(e)},
                    )
                )

        if not executed_any:
            break

    if total_tool_calls >= max_calls:
        activity_log.append(
            record_activity(
                "tool_limit_reached",
                "warning",
                {"max_tool_calls": max_calls},
            )
        )

    # Python-controlled post-processing
    raw_findings = list(findings_map.values())
    validated_findings, validation_warnings = validate_evidence(
        message=message,
        findings=raw_findings,
        guidance_refs=guidance_refs,
        repo=repo,
    )
    for w in validation_warnings:
        activity_log.append(record_activity("evidence_validation", "warning", {"detail": w}))

    # App-controlled deterministic risk scoring
    risk_assessment = assess_risk(
        findings=validated_findings,
        urls_analysis=[u.model_dump() for u in urls_analysis],
        reputation_results=[r.model_dump() for r in reputation_results],
    )
    activity_log.append(
        record_activity(
            "risk_assessment",
            "completed",
            {"level": risk_assessment.level, "score": risk_assessment.score},
        )
    )

    # Highlights and guidance draft
    highlights = build_highlights(validated_findings, message)
    guidance_draft = generate_guidance_draft(
        risk=risk_assessment,
        findings=validated_findings,
        guidance_refs=guidance_refs,
    )

    status = "clarification_needed" if clarification_questions else "ok"

    return {
        "status": status,
        "findings": validated_findings,
        "url_analysis": urls_analysis,
        "reputation": reputation_results,
        "guidance": guidance_refs,
        "attack_sequence": attack_steps,
        "validated_evidence": validated_findings,
        "risk": risk_assessment,
        "highlights": highlights,
        "guidance_draft": guidance_draft,
        "clarification_questions": clarification_questions,
        "activity": activity_log,
    }
