from __future__ import annotations

import random
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.garage import PlayerCar


DEFAULT_SELECTION: dict[str, Any] = {
    "body": "skateboard",
    "wheels": "wheel4",
    "rims": "ice",
    "windows": "clear",
    "paint": "original",
    "rimColor": "ice",
    "windowTint": "clear",
    "stickerColor": "sticker-black",
}

GARAGE_CATEGORIES = [
    {"id": "body", "label": "Көлік", "icon": "▰", "control": "parts"},
    {"id": "rims", "label": "Диск түсі", "icon": "◉", "control": "rims"},
    {"id": "windows", "label": "Әйнек", "icon": "▱", "control": "windows"},
    {"id": "paint", "label": "Бояу", "icon": "◒", "control": "paint"},
    {"id": "stickerColor", "label": "Стикер түсі", "icon": "★", "control": "stickerColor"},
]

GARAGE_PARTS: dict[str, list[dict[str, Any]]] = {
    "body": [
        {"id": "skateboard", "name": "Скейтборд", "model": "/assets/models/body/skateboard.glb", "preview": "/assets/models/body/skateboard.glb", "unlockLevel": 1, "rarity": "legendary"},
        {"id": "e2f-scooter-yellow", "name": "E2F скутері", "model": "/assets/models/body/e2f_scooter_yellow.glb", "preview": "/assets/models/body/e2f_scooter_yellow.glb", "unlockLevel": 1, "rarity": "legendary"},
        {"id": "btwin-triban-100-bike", "name": "BTWIN Triban 100 велосипеді", "model": "/assets/models/body/btwin_triban_100_road_bike.glb", "preview": "/assets/models/body/btwin_triban_100_road_bike.glb", "unlockLevel": 1, "rarity": "legendary"},
        {"id": "ducati-streetfighter-v4-s", "name": "Ducati Streetfighter V4 S мотоциклі", "model": "/assets/models/body/2024_ducati_streetfighter_v4_s.glb", "preview": "/assets/models/body/2024_ducati_streetfighter_v4_s.glb", "unlockLevel": 1, "rarity": "legendary"},
        {"id": "suzuki-quadzilla-500", "name": "Suzuki Quadzilla 500 квадроциклі", "model": "/assets/models/body/suzuki_quadzilla_500.glb", "preview": "/assets/models/body/suzuki_quadzilla_500.glb", "unlockLevel": 1, "rarity": "legendary"},
        {"id": "mini-car-low-poly-v02", "name": "Mini Car Low Poly", "model": "/assets/models/body/mini_car_low_poly_v02.glb", "preview": "/assets/models/body/mini_car_low_poly_v02.glb", "unlockLevel": 1, "rarity": "legendary"},
        {"id": "ford-mustang-shelby-cobra-gt500", "name": "Ford Mustang Shelby Cobra GT500", "model": "/assets/models/body/1967_ford_mustang_shelby_cobra_gt500.glb", "preview": "/assets/models/body/1967_ford_mustang_shelby_cobra_gt500.glb", "unlockLevel": 1, "rarity": "legendary"},
        {"id": "jaguar-project-7", "name": "Project 7 көлігі", "model": "/assets/models/body/jaguar-project-7.glb", "preview": "/car.webp", "unlockLevel": 1, "rarity": "legendary"},
        {"id": "mclaren-720s-spider", "name": "McLaren 720S Spider", "model": "/assets/models/body/mclaren_720s_spider.glb", "preview": "/assets/models/body/mclaren_720s_spider.glb", "unlockLevel": 1, "rarity": "legendary"},
        {"id": "porsche-963-lmdh-hypercar", "name": "Porsche 963 LMDh", "model": "/assets/models/body/porsche_963_lmdh_hypercar.glb", "preview": "/assets/models/body/porsche_963_lmdh_hypercar.glb", "unlockLevel": 1, "rarity": "legendary"},
    ],
    "wheels": [
        {"id": "wheel4", "name": "Turbo Star", "model": "/assets/models/wheels/wheel4.glb", "unlockLevel": 1, "rarity": "rare"},
        {"id": "neon-track", "name": "Neon Track", "model": "/assets/models/wheels/wheel4.glb", "unlockLevel": 5, "rarity": "epic"},
        {"id": "moon-grip", "name": "Moon Grip", "model": "/assets/models/wheels/wheel4.glb", "unlockLevel": 9, "rarity": "legendary"},
    ],
    "paint": [
        {"id": "original", "name": "Бастапқы түс", "unlockLevel": 1},
        {"id": "study-blue", "name": "Оқу көгі", "value": "#21a7ff", "unlockLevel": 1},
        {"id": "quiz-red", "name": "Квиз қызылы", "value": "#ff4f64", "unlockLevel": 1},
        {"id": "coin-gold", "name": "Алтын түс", "value": "#ffc857", "unlockLevel": 3},
        {"id": "mint-boost", "name": "Жалбыз түсі", "value": "#45f0b8", "unlockLevel": 6},
        {"id": "nova-purple", "name": "Күлгін түс", "value": "#8a5cff", "unlockLevel": 10},
    ],
    "rims": [
        {"id": "ice", "name": "Мұз", "value": "#d7f4ff", "unlockLevel": 1},
        {"id": "graphite", "name": "Графит", "value": "#3f4858", "unlockLevel": 1},
        {"id": "sun", "name": "Күн", "value": "#ffcf5c", "unlockLevel": 4},
        {"id": "laser", "name": "Лазер", "value": "#5de2ff", "unlockLevel": 8},
    ],
    "windows": [
        {"id": "clear", "name": "Мөлдір", "value": "#bdefff", "opacity": 0.22, "unlockLevel": 1},
        {"id": "smoke", "name": "Түтін", "value": "#182334", "opacity": 0.48, "unlockLevel": 5},
        {"id": "violet", "name": "Күлгін", "value": "#765cff", "opacity": 0.36, "unlockLevel": 9},
    ],
    "stickerColors": [
        {"id": "sticker-white", "name": "Зауыт ақ түсі", "value": "#f8f4ea", "unlockLevel": 1},
        {"id": "sticker-black", "name": "Карбон қара", "value": "#111827", "unlockLevel": 1},
        {"id": "sticker-red", "name": "Жарыс қызылы", "value": "#ff365f", "unlockLevel": 2},
        {"id": "sticker-gold", "name": "Жеңіс алтыны", "value": "#ffd166", "unlockLevel": 4},
        {"id": "sticker-blue", "name": "Электр көгі", "value": "#36c5ff", "unlockLevel": 6},
    ],
    "stickerColor": [
        {"id": "sticker-white", "name": "Зауыт ақ түсі", "value": "#f8f4ea", "unlockLevel": 1},
        {"id": "sticker-black", "name": "Карбон қара", "value": "#111827", "unlockLevel": 1},
        {"id": "sticker-red", "name": "Жарыс қызылы", "value": "#ff365f", "unlockLevel": 2},
        {"id": "sticker-gold", "name": "Жеңіс алтыны", "value": "#ffd166", "unlockLevel": 4},
        {"id": "sticker-blue", "name": "Электр көгі", "value": "#36c5ff", "unlockLevel": 6},
    ],
}


class GarageService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_config(self) -> dict[str, Any]:
        return {"categories": GARAGE_CATEGORIES, "parts": GARAGE_PARTS, "defaults": DEFAULT_SELECTION}

    async def get_player_car(self, user_id) -> dict[str, Any]:
        row = await self._get_row(user_id)
        if row is None:
            return DEFAULT_SELECTION.copy()
        return {**DEFAULT_SELECTION, **row.customization}

    async def save_player_car(self, user_id, selection: dict[str, Any]) -> dict[str, Any]:
        merged = {**DEFAULT_SELECTION, **selection}
        row = await self._get_row(user_id)
        if row is None:
            row = PlayerCar(user_id=user_id, customization=merged)
            self.session.add(row)
        else:
            row.customization = merged
        await self.session.flush()
        return merged

    def randomize(self, selection: dict[str, Any]) -> dict[str, Any]:
        randomized = {**DEFAULT_SELECTION, **selection}
        for key in ["body", "paint"]:
            randomized[key] = random.choice(GARAGE_PARTS[key])["id"]
        randomized["stickerColor"] = random.choice(GARAGE_PARTS["stickerColors"])["id"]
        randomized["rimColor"] = random.choice(GARAGE_PARTS["rims"])["id"]
        randomized["rims"] = randomized["rimColor"]
        randomized["windowTint"] = random.choice(GARAGE_PARTS["windows"])["id"]
        randomized["windows"] = randomized["windowTint"]
        return randomized

    async def _get_row(self, user_id) -> PlayerCar | None:
        result = await self.session.execute(select(PlayerCar).where(PlayerCar.user_id == user_id))
        return result.scalar_one_or_none()
