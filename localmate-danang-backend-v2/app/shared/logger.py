"""Logger utility for LocalMate - Structured logging for debugging.

Provides colored console logging with structured output for:
- API request/response
- Tool execution
- LLM calls
- Workflow tracing
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any
from dataclasses import dataclass, field, asdict


# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

# Color codes for terminal
COLORS = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "CYAN": "\033[36m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "MAGENTA": "\033[35m",
    "BLUE": "\033[34m",
    "RED": "\033[31m",
}


def colorize(text: str, color: str) -> str:
    """Add color to text for terminal output."""
    return f"{COLORS.get(color, '')}{text}{COLORS['RESET']}"


class LocalMateLogger:
    """Structured logger for LocalMate with colored output."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _format_data(self, data: Any, max_len: int = 500) -> str:
        """Format data for logging, truncating if needed."""
        if data is None:
            return "None"
        
        if isinstance(data, (dict, list)):
            try:
                formatted = json.dumps(data, ensure_ascii=False, default=str)
                if len(formatted) > max_len:
                    return formatted[:max_len] + "..."
                return formatted
            except:
                return str(data)[:max_len]
        
        text = str(data)
        return text[:max_len] + "..." if len(text) > max_len else text
    
    def api_request(self, endpoint: str, method: str, params: dict = None, body: Any = None):
        """Log API request."""
        msg = f"{colorize('→ REQUEST', 'CYAN')} {colorize(method, 'BOLD')} {endpoint}"
        if params:
            msg += f"\n  Params: {self._format_data(params)}"
        if body:
            msg += f"\n  Body: {self._format_data(body)}"
        self.logger.info(msg)
    
    def api_response(self, endpoint: str, status: int, data: Any = None, duration_ms: float = None):
        """Log API response."""
        status_color = "GREEN" if status < 400 else "RED"
        msg = f"{colorize('← RESPONSE', status_color)} {endpoint} [{status}]"
        if duration_ms:
            msg += f" ({duration_ms:.0f}ms)"
        if data:
            msg += f"\n  Data: {self._format_data(data)}"
        self.logger.info(msg)
    
    def tool_call(self, tool_name: str, arguments: dict):
        """Log tool call start."""
        msg = f"{colorize('🔧 TOOL', 'MAGENTA')} {colorize(tool_name, 'BOLD')}"
        msg += f"\n  Args: {self._format_data(arguments)}"
        self.logger.info(msg)
    
    def tool_result(self, tool_name: str, result_count: int, sample: Any = None):
        """Log tool result."""
        msg = f"{colorize('✓ RESULT', 'GREEN')} {tool_name} → {result_count} results"
        if sample:
            msg += f"\n  Sample: {self._format_data(sample, max_len=200)}"
        self.logger.info(msg)
    
    def llm_call(self, provider: str, model: str, prompt_preview: str = None):
        """Log LLM call."""
        msg = f"{colorize('🤖 LLM', 'BLUE')} {provider}/{model}"
        if prompt_preview:
            preview = prompt_preview[:100] + "..." if len(prompt_preview) > 100 else prompt_preview
            msg += f"\n  Prompt: {preview}"
        self.logger.info(msg)
    
    def llm_response(self, provider: str, response_preview: str = None, tokens: int = None):
        """Log LLM response."""
        msg = f"{colorize('💬 LLM RESPONSE', 'BLUE')} {provider}"
        if tokens:
            msg += f" ({tokens} tokens)"
        if response_preview:
            preview = response_preview[:150] + "..." if len(response_preview) > 150 else response_preview
            msg += f"\n  Response: {preview}"
        self.logger.info(msg)
    
    def workflow_step(self, step: str, details: str = None):
        """Log workflow step."""
        msg = f"{colorize('▶', 'YELLOW')} {step}"
        if details:
            msg += f": {details}"
        self.logger.info(msg)
    
    def error(self, message: str, error: Exception = None):
        """Log error."""
        msg = f"{colorize('❌ ERROR', 'RED')} {message}"
        if error:
            msg += f"\n  {type(error).__name__}: {str(error)}"
        self.logger.error(msg)
    
    def debug(self, message: str, data: Any = None):
        """Log debug info."""
        msg = f"{colorize('DEBUG', 'CYAN')} {message}"
        if data:
            msg += f": {self._format_data(data)}"
        self.logger.debug(msg)


@dataclass
class WorkflowStep:
    """A step in the agent workflow."""
    
    step_name: str
    tool_name: str | None = None
    purpose: str = ""
    input_summary: str = ""
    output_summary: str = ""
    result_count: int = 0
    duration_ms: float = 0


@dataclass
class AgentWorkflow:
    """Complete workflow trace for a chat request."""
    
    query: str
    intent_detected: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    total_duration_ms: float = 0
    tools_used: list[str] = field(default_factory=list)
    
    def add_step(self, step: WorkflowStep):
        """Add a step to the workflow."""
        self.steps.append(step)
        if step.tool_name and step.tool_name not in self.tools_used:
            self.tools_used.append(step.tool_name)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "query": self.query,
            "intent_detected": self.intent_detected,
            "tools_used": self.tools_used,
            "steps": [
                {
                    "step": s.step_name,
                    "tool": s.tool_name,
                    "purpose": s.purpose,
                    "results": s.result_count,
                }
                for s in self.steps
            ],
            "total_duration_ms": round(self.total_duration_ms, 1),
        }
    
    def to_summary(self) -> str:
        """Generate human-readable workflow summary."""
        lines = [f"📊 **Workflow Summary**"]
        lines.append(f"- Query: \"{self.query[:50]}{'...' if len(self.query) > 50 else ''}\"")
        lines.append(f"- Intent: {self.intent_detected}")
        lines.append(f"- Tools: {', '.join(self.tools_used) or 'None'}")
        
        if self.steps:
            lines.append("\n**Steps:**")
            for i, step in enumerate(self.steps, 1):
                tool_info = f" ({step.tool_name})" if step.tool_name else ""
                results_info = f" → {step.result_count} results" if step.result_count else ""
                lines.append(f"{i}. {step.step_name}{tool_info}{results_info}")
        
        lines.append(f"\n⏱️ Total: {self.total_duration_ms:.0f}ms")
        return "\n".join(lines)


# Global logger instances
agent_logger = LocalMateLogger("agent")
api_logger = LocalMateLogger("api")
tool_logger = LocalMateLogger("tools")
