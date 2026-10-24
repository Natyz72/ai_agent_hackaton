from typing import Any
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

        # Default multi-step investigation behavior
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        if self.call_count == 1:
            return LLMResponse(
                tool_calls=[
                    ToolCall(name="inspect_indicators", arguments={"message": last_user_msg}),
                    ToolCall(name="analyze_url_structure", arguments={"message": last_user_msg}),
                ]
            )
        elif self.call_count == 2:
            return LLMResponse(
                tool_calls=[
                    ToolCall(name="detect_social_engineering", arguments={"message": last_user_msg}),
                    ToolCall(name="check_domain_reputation", arguments={"hostnames": ["example.com"]}),
                ]
            )
        elif self.call_count == 3:
            return LLMResponse(
                tool_calls=[
                    ToolCall(name="search_guidance", arguments={"query": "phishing urgency credentials"}),
                    ToolCall(name="map_attack_sequence", arguments={"message": last_user_msg, "findings": []}),
                ]
            )
        else:
            return LLMResponse(content="Analysis concluded based on tool findings.")
