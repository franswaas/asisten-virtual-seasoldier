"""
Logging, Analytics, and Lifecycle Hooks for Asisten Virtual Seasoldier.
Logs interactions, tool invocations, user feedback, and runtime errors to JSON Lines.
"""

import json
import logging
import os
import time
from datetime import datetime

logger = logging.getLogger("seasoldier_assistant")

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def _get_log_filepath(prefix: str) -> str:
    """Get log filepath with current date."""
    date_str = datetime.now().strftime("%Y%m%d")
    return os.path.join(LOG_DIR, f"{prefix}_{date_str}.jsonl")


def _append_jsonl(filepath: str, data: dict) -> None:
    """Safely append a dictionary as a JSON line."""
    try:
        data["timestamp"] = datetime.now().isoformat()
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to write log to {filepath}: {e}")


def log_interaction(
    session_id: str,
    question: str,
    answer: str,
    model: str,
    duration_ms: int,
    tool_calls: list | None = None,
) -> None:
    """Log an interaction between user and assistant."""
    filepath = _get_log_filepath("interactions")
    _append_jsonl(filepath, {
        "event": "chat_interaction",
        "session_id": session_id,
        "question": question,
        "answer_length": len(answer),
        "model": model,
        "duration_ms": duration_ms,
        "tool_calls_count": len(tool_calls) if tool_calls else 0,
        "tool_calls": tool_calls or [],
    })


def log_tool_call(tool_name: str, arguments: dict, result_length: int) -> None:
    """Log a tool function invocation."""
    filepath = _get_log_filepath("tool_calls")
    _append_jsonl(filepath, {
        "event": "tool_call",
        "tool_name": tool_name,
        "arguments": arguments,
        "result_length": result_length,
    })


def log_error(session_id: str, error_type: str, message: str, details: str = "") -> None:
    """Log an application error."""
    filepath = _get_log_filepath("errors")
    _append_jsonl(filepath, {
        "event": "error",
        "session_id": session_id,
        "error_type": error_type,
        "message": message,
        "details": details,
    })


def log_feedback(session_id: str, message_id: str, rating: str, comment: str = "") -> None:
    """Log user feedback (thumbs up / thumbs down)."""
    filepath = _get_log_filepath("feedback")
    _append_jsonl(filepath, {
        "event": "feedback",
        "session_id": session_id,
        "message_id": message_id,
        "rating": rating,
        "comment": comment,
    })


def get_daily_stats() -> dict:
    """Get summarized interaction statistics for today."""
    filepath = _get_log_filepath("interactions")
    if not os.path.exists(filepath):
        return {"total_questions": 0, "avg_duration_ms": 0, "total_tools_used": 0}

    total_questions = 0
    total_duration = 0
    total_tools = 0

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    total_questions += 1
                    total_duration += record.get("duration_ms", 0)
                    total_tools += record.get("tool_calls_count", 0)

        avg_dur = round(total_duration / total_questions) if total_questions > 0 else 0
        return {
            "total_questions": total_questions,
            "avg_duration_ms": avg_dur,
            "total_tools_used": total_tools,
        }
    except Exception as e:
        logger.error(f"Error computing daily stats: {e}")
        return {"total_questions": 0, "avg_duration_ms": 0, "total_tools_used": 0}
