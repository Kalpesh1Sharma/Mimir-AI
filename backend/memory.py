# backend/memory.py

from typing import Dict, List, Optional


class MemoryManager:
    """
    Manages short-term conversational memory.

    Memory is session-scoped and used only to provide
    conversational context, not for training.
    """

    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self._sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_context(self, session_id: Optional[str]) -> Optional[str]:
        """
        Retrieve formatted conversational context for a session.
        """
        if not session_id or session_id not in self._sessions:
            return None

        turns = self._sessions[session_id][-self.max_turns :]
        return self._format_context(turns)

    def update(
        self,
        session_id: Optional[str],
        user_input: str,
        assistant_output: str,
    ) -> None:
        """
        Update session memory with a new interaction.
        """
        if not session_id:
            return

        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append(
            {
                "user": user_input,
                "assistant": assistant_output,
            }
        )

    def clear(self, session_id: str) -> None:
        """
        Clear memory for a session.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

    def _format_context(self, turns: List[Dict[str, str]]) -> str:
        """
        Convert turns into a compact context string.
        """
        context_lines = []

        for turn in turns:
            context_lines.append(f"User: {turn['user']}")
            context_lines.append(f"Assistant: {turn['assistant']}")

        return "\n".join(context_lines)
