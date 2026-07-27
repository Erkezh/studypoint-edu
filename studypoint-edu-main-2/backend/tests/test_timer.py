from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.services.timer_service import apply_active_time_delta, inactivity_threshold_seconds_for_grade


def test_inactivity_threshold_by_grade():
    assert inactivity_threshold_seconds_for_grade(None) == 240
    assert inactivity_threshold_seconds_for_grade(-1) == 120
    assert inactivity_threshold_seconds_for_grade(2) == 120
    assert inactivity_threshold_seconds_for_grade(3) == 240
    assert inactivity_threshold_seconds_for_grade(8) == 240
    assert inactivity_threshold_seconds_for_grade(9) == 360


def test_active_time_caps_on_inactivity():
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    active, last = apply_active_time_delta(
        last_activity_at=t0,
        now=t0 + timedelta(seconds=1000),
        inactivity_threshold_seconds=240,
        current_active_time_seconds=0,
    )
    assert active == 240
    assert last == t0 + timedelta(seconds=1000)


def test_active_time_accumulates_small_bursts():
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    active, last = apply_active_time_delta(
        last_activity_at=t0,
        now=t0 + timedelta(seconds=10),
        inactivity_threshold_seconds=240,
        current_active_time_seconds=0,
    )
    active, last = apply_active_time_delta(
        last_activity_at=last,
        now=last + timedelta(seconds=15),
        inactivity_threshold_seconds=240,
        current_active_time_seconds=active,
    )
    assert active == 25

