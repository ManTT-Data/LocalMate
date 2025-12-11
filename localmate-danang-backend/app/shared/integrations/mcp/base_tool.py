"""Base MCP Tool - Abstract base class for all MCP tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ToolStatus(str, Enum):
    """Status of tool execution."""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class ToolResult:
    """Result from tool execution."""

    status: ToolStatus
    data: dict[str, Any] | None = None
    error: str | None = None


class MCPBaseTool(ABC):
    """
    Abstract base class for MCP tools.

    All MCP tools (Grab, Agoda, Klook, etc.) should inherit from this.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the tool."""
        pass

    @abstractmethod
    def get_tool_spec(self) -> dict:
        """
        Get tool specification for LLM function calling.

        Returns:
            OpenAI-style function spec dict
        """
        pass

    @abstractmethod
    async def execute(self, params: dict) -> ToolResult:
        """
        Execute the tool with given parameters.

        Args:
            params: Tool-specific parameters

        Returns:
            ToolResult with status and data
        """
        pass

    async def validate_params(self, params: dict) -> tuple[bool, str | None]:
        """
        Validate parameters before execution.

        Args:
            params: Parameters to validate

        Returns:
            (is_valid, error_message)
        """
        return True, None
