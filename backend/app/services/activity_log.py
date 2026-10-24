import uuid
from datetime import datetime, timezone
from typing import Any
from app.schemas.common import ActivityEvent


def record_activity(
    event_type: str,
    status: str,
    detail: dict[str, Any] | None = None,
) -> ActivityEvent:
    """
    Creates a truthful, timestamped activity event record.
    Never fabricates events that did not occur.
    """
    return ActivityEvent(
        id=str(uuid.uuid4()),
        type=event_type,
        status=status,
        detail=detail or {},
        timestamp=datetime.now(timezone.utc),
    )
