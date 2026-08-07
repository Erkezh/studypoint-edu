from app.services.practice_service import _plugin_difficulty_transition


def test_plugin_level_increases_after_two_correct_answers():
    first = _plugin_difficulty_transition(
        level=2, correct_streak=0, wrong_streak=1, is_correct=True
    )
    assert first == (2, 1, 0)

    second = _plugin_difficulty_transition(
        level=first[0], correct_streak=first[1], wrong_streak=first[2], is_correct=True
    )
    assert second == (3, 0, 0)


def test_plugin_level_decreases_after_three_wrong_answers():
    first = _plugin_difficulty_transition(
        level=3, correct_streak=1, wrong_streak=0, is_correct=False
    )
    second = _plugin_difficulty_transition(
        level=first[0], correct_streak=first[1], wrong_streak=first[2], is_correct=False
    )
    third = _plugin_difficulty_transition(
        level=second[0], correct_streak=second[1], wrong_streak=second[2], is_correct=False
    )

    assert first == (3, 0, 1)
    assert second == (3, 0, 2)
    assert third == (2, 0, 0)


def test_plugin_level_stays_within_bounds():
    assert _plugin_difficulty_transition(
        level=5, correct_streak=1, wrong_streak=0, is_correct=True
    ) == (5, 0, 0)
    assert _plugin_difficulty_transition(
        level=1, correct_streak=0, wrong_streak=2, is_correct=False
    ) == (1, 0, 0)
