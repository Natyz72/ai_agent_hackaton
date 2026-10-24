from typing import Any
import re
from app.llm.base import LLMClient, LLMResponse, ToolCall


class FakeLLMClient(LLMClient):
    """
    Deterministic Fake LLM Client for testing and offline development.
    Can be configured with scripted responses or uses a standard tool sequence.
    """

    def __init__(
        self,
        scripted_responses: list[LLMResponse] | None = None,
        simulate_error: bool = False,
    ):
        self.scripted_responses = list(scripted_responses) if scripted_responses else None
        self.simulate_error = simulate_error
        self.call_count = 0
        self.history: list[dict[str, Any]] = []

    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        system_instruction: str | None = None,
    ) -> LLMResponse:
        self.history.append({"messages": messages, "tools": tools, "system": system_instruction})
        self.call_count += 1

        if self.simulate_error:
            raise RuntimeError("Simulated LLM Provider Failure")

        if self.scripted_responses is not None:
            if self.scripted_responses:
                return self.scripted_responses.pop(0)
            return LLMResponse(content="Investigation complete.")

        # Default multi-step investigation behavior: extract original submitted message
        original_user_msg = ""
        for m in messages:
            if m.get("role") == "user" and m.get("content"):
                original_user_msg = m.get("content", "")
                break

        # Extract hostnames from message for domain check
        found_hosts = []
        for match in re.finditer(r"(?:https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", original_user_msg):
            host = match.group(1).split("@")[-1].split(":")[0].lower()
            if host and host not in found_hosts:
                found_hosts.append(host)
        if not found_hosts:
            found_hosts = ["example.com"]

        if self.call_count == 1:
            return LLMResponse(
                tool_calls=[
                    ToolCall(name="inspect_indicators", arguments={"message": original_user_msg}),
                    ToolCall(name="analyze_url_structure", arguments={"message": original_user_msg}),
                ]
            )
        elif self.call_count == 2:
            return LLMResponse(
                tool_calls=[
                    ToolCall(name="detect_social_engineering", arguments={"message": original_user_msg}),
                    ToolCall(name="check_domain_reputation", arguments={"hostnames": found_hosts}),
                ]
            )
        elif self.call_count == 3:
            return LLMResponse(
                tool_calls=[
                    ToolCall(name="search_guidance", arguments={"query": "phishing urgency credentials"}),
                    ToolCall(name="map_attack_sequence", arguments={"message": original_user_msg, "findings": []}),
                ]
            )
        else:
            return LLMResponse(content="Analysis concluded based on tool findings.")
