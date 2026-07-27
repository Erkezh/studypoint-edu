from app.services.gamification_service import GamificationService, calculate_level, character_item_progression


def test_progression_supports_twelve_levels() -> None:
    assert calculate_level(0) == 1
    assert calculate_level(6999) == 9
    assert calculate_level(7000) == 10
    assert calculate_level(8799) == 10
    assert calculate_level(8800) == 11
    assert calculate_level(10899) == 11
    assert calculate_level(10900) == 12
    assert calculate_level(999999) == 12


def test_next_level_threshold_stops_at_level_twelve() -> None:
    assert GamificationService.next_level_xp(10) == 8800
    assert GamificationService.next_level_xp(11) == 10900
    assert GamificationService.next_level_xp(12) == 10900


def test_character_catalog_spans_full_progression() -> None:
    assert character_item_progression("default-boy", "characters") == (1, 0)
    assert character_item_progression("jackal", "characters")[0] == 12
    assert character_item_progression("Body_BasicBody", "body") == (1, 0)
    level, price = character_item_progression("Overall_SmartDress", "overall")
    assert 6 <= level <= 12
    assert price > 0
