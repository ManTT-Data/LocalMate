"""Agent State Models - State management for ReAct multi-step reasoning."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ReActStep:
    """A single step in the ReAct reasoning loop."""
    
    step_number: int
    thought: str  # LLM's reasoning about what to do
    action: str  # Tool name or "finish"
    action_input: dict  # Tool arguments
    observation: Any = None  # Tool result
    duration_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "step": self.step_number,
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self._truncate_observation(),
            "duration_ms": round(self.duration_ms, 1),
        }
    
    def _truncate_observation(self, max_items: int = 3) -> Any:
        """Truncate observation for display."""
        if isinstance(self.observation, list) and len(self.observation) > max_items:
            return self.observation[:max_items] + [f"... and {len(self.observation) - max_items} more"]
        return self.observation


@dataclass
class AgentState:
    """Complete state for a ReAct agent session."""
    
    query: str
    steps: list[ReActStep] = field(default_factory=list)
    context: dict = field(default_factory=dict)  # Accumulated context from tools
    current_step: int = 0
    max_steps: int = 5
    is_complete: bool = False
    final_answer: str = ""
    selected_place_ids: list[str] = field(default_factory=list)  # LLM-selected places
    total_duration_ms: float = 0
    error: str | None = None
    
    def add_step(self, step: ReActStep) -> None:
        """Add a completed step to the state."""
        self.steps.append(step)
        self.current_step += 1
        
        # Add tool result to context
        if step.action != "finish" and step.observation:
            self.context[step.action] = step.observation
    
    def can_continue(self) -> bool:
        """Check if agent can continue reasoning."""
        return (
            not self.is_complete
            and self.current_step < self.max_steps
            and self.error is None
        )
    
    def get_context_summary(self) -> str:
        """Get a summary of accumulated context for LLM."""
        if not self.context:
            return "Chưa có kết quả từ các tools trước đó."
        
        summary_parts = []
        for tool_name, result in self.context.items():
            if isinstance(result, list):
                summary_parts.append(f"- {tool_name}: {len(result)} kết quả")
            elif isinstance(result, dict):
                summary_parts.append(f"- {tool_name}: {result}")
            else:
                summary_parts.append(f"- {tool_name}: {str(result)[:100]}")
        
        return "Kết quả từ các bước trước:\n" + "\n".join(summary_parts)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "query": self.query,
            "total_steps": len(self.steps),
            "max_steps": self.max_steps,
            "is_complete": self.is_complete,
            "steps": [s.to_dict() for s in self.steps],
            "tools_used": list(self.context.keys()),
            "total_duration_ms": round(self.total_duration_ms, 1),
            "error": self.error,
        }
