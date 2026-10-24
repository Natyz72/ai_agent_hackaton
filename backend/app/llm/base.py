from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)


class LLMClient(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        system_instruction: str | None = None,
    ) -> LLMResponse:
        """
        Generate a response or tool calls given message history and available tool schemas.
        """
        pass
