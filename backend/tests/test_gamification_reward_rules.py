from app.services.gamification_service import coins_for_correct_answer


def test_correct_answer_awards_one_base_coin():
    assert coins_for_correct_answer(True) == 1


def test_wrong_answer_awards_no_base_coins():
    assert coins_for_correct_answer(False) == 0
