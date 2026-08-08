"""Session and conversation memory management for SupportFlow AI.

Designed with an interface that effortlessly transitions from in-memory (Phase 1)
to PostgreSQL checkpointers (Phase 3).
"""
from typing import Dict, Any, Optional, List
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage


class MemoryManager:
    """Manages LangGraph checkpointers and multi-turn session states."""

    def __init__(self, checkpointer: Optional[Any] = None):
        self._checkpointer = checkpointer or MemorySaver()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}

    @property
    def checkpointer(self) -> Any:
        return self._checkpointer

    def get_thread_config(self, thread_id: str) -> Dict[str, Any]:
        """Returns the execution config dict required by LangGraph for a specific thread."""
        return {"configurable": {"thread_id": thread_id}}

    def record_session_metadata(self, thread_id: str, metadata: Dict[str, Any]) -> None:
        """Stores thread-level metadata (e.g. user_id, channel, start_time)."""
        if thread_id not in self._active_sessions:
            self._active_sessions[thread_id] = {}
        self._active_sessions[thread_id].update(metadata)

    def get_session_metadata(self, thread_id: str) -> Dict[str, Any]:
        """Retrieves stored metadata for an active session."""
        return self._active_sessions.get(thread_id, {})


# Global memory manager instance
_global_memory_manager = MemoryManager()


def get_checkpointer() -> Any:
    """Retrieves the default checkpointer for graph compilation."""
    return _global_memory_manager.checkpointer


def get_memory_manager() -> MemoryManager:
    """Retrieves the singleton MemoryManager instance."""
    return _global_memory_manager
