import pytest
from app.agent.loop import run_investigation_loop
from app.llm.base import LLMResponse, ToolCall
from app.llm.fake import FakeLLMClient


class MockRepo:
    def __init__(self):
        self.passages = {
            "SEC-01": {"id": "SEC-01", "title": "Verify sender identity", "content": "Always verify sender."}
        }

    def get_domain_reputation(self, hostname: str):
        if hostname == "phishy.example":
            return {"hostname": hostname, "status": "suspicious", "source": "test", "reason": "Flagged"}
        return None

    def get_trusted_domains(self):
        return [{"domain": "example.com", "reason": "trusted"}]

    def search_guidance(self, query: str):
        return list(self.passages.values())

    def get_guidance_by_id(self, gid: str):
        return self.passages.get(gid)


@pytest.mark.asyncio
async def test_agent_loop_normal_sequence():
    message = "Urgent! Your account at company.example is suspended. Login at hxxp://evil.example now."
    llm = FakeLLMClient()
    repo = MockRepo()

    result = await run_investigation_loop(message, llm, repo=repo)

    assert result["status"] == "ok"
    assert len(result["findings"]) > 0
    assert result["risk"] is not None
    assert result["risk"].level in ("low", "medium", "high")
    assert len(result["guidance_draft"]) > 0
    assert len(result["activity"]) > 0


@pytest.mark.asyncio
async def test_agent_loop_enforces_tool_cap():
    message = "Test message"
    # Create scripted responses that continuously issue tool calls
    infinite_calls = [
        LLMResponse(tool_calls=[ToolCall(name="inspect_indicators", arguments={"message": f"call_{i}"})])
        for i in range(10)
    ]
    llm = FakeLLMClient(scripted_responses=infinite_calls)
    repo = MockRepo()

    result = await run_investigation_loop(message, llm, repo=repo)

    # Must terminate without error and have tool_limit_reached activity event
    assert any(a.type == "tool_limit_reached" for a in result["activity"])


@pytest.mark.asyncio
async def test_agent_loop_rejects_unauthorized_tool():
    message = "Test message"
    # Attempt to invoke create_incident through the model
    malicious_call = [
        LLMResponse(
            tool_calls=[
                ToolCall(name="create_incident", arguments={"title": "Hacked"}),
                ToolCall(name="inspect_indicators", arguments={"message": message}),
            ]
        ),
        LLMResponse(content="Done"),
    ]
    llm = FakeLLMClient(scripted_responses=malicious_call)
    repo = MockRepo()

    result = await run_investigation_loop(message, llm, repo=repo)

    # create_incident should be rejected in activity log
    rejected_events = [a for a in result["activity"] if a.type == "tool_execution" and a.status == "rejected"]
    assert len(rejected_events) == 1
    assert rejected_events[0].detail.get("tool") == "create_incident"


@pytest.mark.asyncio
async def test_agent_loop_skips_duplicate_tool_call():
    message = "Test message"
    dup_calls = [
        LLMResponse(
            tool_calls=[
                ToolCall(name="inspect_indicators", arguments={"message": message}),
                ToolCall(name="inspect_indicators", arguments={"message": message}),
            ]
        ),
        LLMResponse(content="Done"),
    ]
    llm = FakeLLMClient(scripted_responses=dup_calls)
    repo = MockRepo()

    result = await run_investigation_loop(message, llm, repo=repo)

    dup_events = [a for a in result["activity"] if a.status == "skipped_duplicate"]
    assert len(dup_events) == 1


@pytest.mark.asyncio
async def test_agent_loop_clarification():
    message = "hi"
    clarification_response = [
        LLMResponse(
            clarification_questions=["Can you provide the full message headers or content?"]
        )
    ]
    llm = FakeLLMClient(scripted_responses=clarification_response)
    repo = MockRepo()

    result = await run_investigation_loop(message, llm, repo=repo)

    assert result["status"] == "clarification_needed"
    assert len(result["clarification_questions"]) == 1


@pytest.mark.asyncio
async def test_agent_loop_handles_llm_failure():
    message = "Test message"
    llm = FakeLLMClient(simulate_error=True)
    repo = MockRepo()

    # Loop should not crash; it logs failure and returns safe assessment
    result = await run_investigation_loop(message, llm, repo=repo)

    assert any(a.status == "failed" for a in result["activity"])
    assert result["risk"] is not None
