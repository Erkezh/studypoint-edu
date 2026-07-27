from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.enums import PracticeZone


@dataclass(frozen=True)
class WindowStats:
    correct: int
    total: int

    @property
    def accuracy(self) -> float:
        if self.total <= 0:
            return 1.0
        return self.correct / self.total


@dataclass(frozen=True)
class ScoreResult:
    smartscore: int
    streak: int
    zone: PracticeZone
    delta: int


def zone_for_score(score: int) -> PracticeZone:
    if score >= 90:
        return PracticeZone.CHALLENGE
    if score >= 70:
        return PracticeZone.REFINING
    return PracticeZone.LEARNING


def required_streak_for_mastery(question_level: int) -> int:
    lvl = max(1, min(5, int(question_level)))
    return {1: 6, 2: 7, 3: 8, 4: 9, 5: 10}[lvl]


def compute_next_smartscore(
    *,
    current_smartscore: int,
    zone: PracticeZone | None,
    question_level: int,
    is_correct: bool,
    current_streak: int,
    wrong_streak: int = 0,  # Серия неправильных ответов подряд
    recent_window_stats: WindowStats | None = None,
) -> ScoreResult:
    score_before = int(max(0, min(100, current_smartscore)))
    zone_before = zone or zone_for_score(score_before)
    lvl = max(1, min(5, int(question_level)))
    streak_before = max(0, int(current_streak))
    wrong_streak_before = max(0, int(wrong_streak))

    # Новая логика:
    # Правильные ответы: первый +15, второй +14, третий +13 и т.д. (уменьшается на 1)
    # Неправильные ответы: первый -1, второй -2, третий -3 и т.д. (увеличивается отрицательное значение)
    
    if is_correct:
        # Правильный ответ: серия правильных увеличивается, серия неправильных сбрасывается
        streak_after = streak_before + 1
        wrong_streak_after = 0
        # Первый правильный: +15, второй: +14, третий: +13 и т.д.
        # Минимум +1 (чтобы не было отрицательных или нулевых приростов)
        delta = max(1, 16 - streak_after)  # 16 - 1 = 15, 16 - 2 = 14, и т.д.
    else:
        # Неправильный ответ: серия правильных сбрасывается, серия неправильных увеличивается
        streak_after = 0
        wrong_streak_after = wrong_streak_before + 1
        # Первый неправильный: -1, второй: -2, третий: -3 и т.д.
        delta = -wrong_streak_after  # -1, -2, -3, и т.д.

    score_after = max(0, min(100, score_before + delta))
    zone_after = zone_for_score(score_after)

    return ScoreResult(smartscore=score_after, streak=streak_after, zone=zone_after, delta=delta)

