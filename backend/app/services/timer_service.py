from __future__ import annotations

from datetime import datetime

from app.utils.time import utc_now


def inactivity_threshold_seconds_for_grade(grade_level: int | None) -> int:
    if grade_level is None:
        return 240
    if grade_level <= 2:
        return 120
    if grade_level <= 8:
        return 240
    return 360


def apply_active_time_delta(
    *,
    last_activity_at: datetime,
    now: datetime | None = None,
    inactivity_threshold_seconds: int,
    current_active_time_seconds: int,
) -> tuple[int, datetime]:
    now_ts = now or utc_now()
    delta = int((now_ts - last_activity_at).total_seconds())
    if delta <= 0:
        return current_active_time_seconds, now_ts
    capped = min(delta, int(inactivity_threshold_seconds))
    return current_active_time_seconds + capped, now_ts

