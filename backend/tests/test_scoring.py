from __future__ import annotations

import pytest

from app.models.enums import PracticeZone
from app.services.scoring import WindowStats, compute_next_smartscore, required_streak_for_mastery, zone_for_score


def test_zone_transitions():
    assert zone_for_score(0) == PracticeZone.LEARNING
    assert zone_for_score(69) == PracticeZone.LEARNING
    assert zone_for_score(70) == PracticeZone.REFINING
    assert zone_for_score(89) == PracticeZone.REFINING
    assert zone_for_score(90) == PracticeZone.CHALLENGE
    assert zone_for_score(100) == PracticeZone.CHALLENGE


@pytest.mark.parametrize("level", [1, 2, 3, 4, 5])
def test_challenge_zone_deltas(level: int):
    base = 95
    r1 = compute_next_smartscore(
        current_smartscore=base,
        zone=PracticeZone.CHALLENGE,
        question_level=level,
        is_correct=True,
        current_streak=0,
        recent_window_stats=WindowStats(correct=10, total=10),
    )
    assert r1.delta in {1, 2}
    assert r1.zone == PracticeZone.CHALLENGE

    r2 = compute_next_smartscore(
        current_smartscore=base,
        zone=PracticeZone.CHALLENGE,
        question_level=level,
        is_correct=False,
        current_streak=3,
        recent_window_stats=WindowStats(correct=10, total=10),
    )
    assert -8 <= r2.delta <= -3
    assert r2.streak == 0


def test_mastery_requires_streak_in_challenge_zone():
    level = 5
    req = required_streak_for_mastery(level)

    # From 99, correct without enough streak should not reach 100.
    r1 = compute_next_smartscore(
        current_smartscore=99,
        zone=PracticeZone.CHALLENGE,
        question_level=level,
        is_correct=True,
        current_streak=req - 3,
        recent_window_stats=WindowStats(correct=10, total=10),
    )
    assert r1.smartscore == 99

    # With required streak, it can reach 100.
    r2 = compute_next_smartscore(
        current_smartscore=99,
        zone=PracticeZone.CHALLENGE,
        question_level=level,
        is_correct=True,
        current_streak=req - 1,
        recent_window_stats=WindowStats(correct=10, total=10),
    )
    assert r2.smartscore == 100

