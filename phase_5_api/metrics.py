import json
import os
from datetime import datetime, timezone

METRICS_FILE = os.path.join(os.path.dirname(__file__), '..', 'metrics.json')


def record_note_copy(session_id: str, idea_title: str, user_location: str = None) -> dict:
    """Record a note copy event and return updated metrics."""
    metrics = _load()

    event = {
        "event": "note_copied",
        "session_id": session_id,
        "idea_title": idea_title,
        "user_location": user_location,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    metrics["events"].append(event)
    metrics["total_note_copies"] += 1

    # Per-idea count
    if "per_idea" not in metrics:
        metrics["per_idea"] = {}
    metrics["per_idea"][idea_title] = metrics["per_idea"].get(idea_title, 0) + 1

    _save(metrics)
    return {
        "total_note_copies": metrics["total_note_copies"],
        "this_idea_copies": metrics["per_idea"][idea_title]
    }


def get_metrics() -> dict:
    """Return a summary of all tracked metrics."""
    metrics = _load()
    return {
        "total_note_copies": metrics.get("total_note_copies", 0),
        "per_idea_copies": metrics.get("per_idea", {}),
        "total_events": len(metrics.get("events", [])),
        "recent_events": metrics.get("events", [])[-10:]  # last 10
    }


def _load() -> dict:
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"events": [], "total_note_copies": 0, "per_idea": {}}


def _save(metrics: dict):
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)
