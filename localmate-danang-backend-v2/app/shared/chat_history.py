"""Chat history manager for per-user conversation storage."""

from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class ChatMessage:
    """Single chat message."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ChatSession:
    """Chat session with history."""

    session_id: str
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to this session."""
        self.messages.append(ChatMessage(role=role, content=content))

    def get_history_text(self, max_messages: int = 10) -> str:
        """Get formatted history for prompt injection."""
        recent = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        if not recent:
            return ""

        lines = []
        for msg in recent:
            prefix = "User" if msg.role == "user" else "Assistant"
            lines.append(f"{prefix}: {msg.content}")

        return "\n".join(lines)


class ChatHistoryManager:
    """
    Manages chat history per user with multiple sessions.

    Each user can have up to max_sessions active sessions.
    Oldest sessions are removed when limit is exceeded.
    """

    def __init__(self, max_sessions_per_user: int = 3, max_messages_per_session: int = 20):
        """
        Initialize the chat history manager.

        Args:
            max_sessions_per_user: Maximum sessions to keep per user (default 3)
            max_messages_per_session: Maximum messages per session (default 20)
        """
        self.max_sessions = max_sessions_per_user
        self.max_messages = max_messages_per_session
        self._sessions: dict[str, dict[str, ChatSession]] = defaultdict(dict)

    def get_or_create_session(self, user_id: str, session_id: str | None = None) -> ChatSession:
        """
        Get existing session or create a new one.

        Args:
            user_id: User identifier
            session_id: Optional session ID (uses "default" if not provided)

        Returns:
            ChatSession instance
        """
        session_id = session_id or "default"
        user_sessions = self._sessions[user_id]

        if session_id not in user_sessions:
            # Create new session
            user_sessions[session_id] = ChatSession(session_id=session_id)

            # Enforce max sessions limit
            if len(user_sessions) > self.max_sessions:
                # Remove oldest session
                oldest_id = min(
                    user_sessions.keys(),
                    key=lambda k: user_sessions[k].created_at
                )
                del user_sessions[oldest_id]

        return user_sessions[session_id]

    def add_message(
        self,
        user_id: str,
        role: str,
        content: str,
        session_id: str | None = None,
    ) -> None:
        """
        Add a message to user's session.

        Args:
            user_id: User identifier
            role: "user" or "assistant"
            content: Message content
            session_id: Optional session ID
        """
        session = self.get_or_create_session(user_id, session_id)
        session.add_message(role, content)

        # Enforce max messages per session
        if len(session.messages) > self.max_messages:
            session.messages = session.messages[-self.max_messages:]

    def get_history(
        self,
        user_id: str,
        session_id: str | None = None,
        max_messages: int = 10,
    ) -> str:
        """
        Get formatted chat history for prompt.

        Args:
            user_id: User identifier
            session_id: Optional session ID
            max_messages: Maximum messages to include

        Returns:
            Formatted history string
        """
        session = self.get_or_create_session(user_id, session_id)
        return session.get_history_text(max_messages)

    def get_messages(
        self,
        user_id: str,
        session_id: str | None = None,
    ) -> list[ChatMessage]:
        """Get all messages for a session."""
        session = self.get_or_create_session(user_id, session_id)
        return session.messages

    def clear_session(self, user_id: str, session_id: str | None = None) -> None:
        """Clear a specific session."""
        session_id = session_id or "default"
        if user_id in self._sessions and session_id in self._sessions[user_id]:
            del self._sessions[user_id][session_id]

    def clear_all_sessions(self, user_id: str) -> None:
        """Clear all sessions for a user."""
        if user_id in self._sessions:
            self._sessions[user_id].clear()

    def get_session_ids(self, user_id: str) -> list[str]:
        """Get all session IDs for a user."""
        return list(self._sessions.get(user_id, {}).keys())


# Global chat history manager instance
chat_history = ChatHistoryManager(max_sessions_per_user=3, max_messages_per_session=20)
