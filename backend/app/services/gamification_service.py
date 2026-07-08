from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.gamification import (
    GarageItem,
    SelectedVehicleCustomization,
    StudentGamification,
    StudentGarageItem,
    StudentVehicle,
    Vehicle,
)
from app.utils.time import utc_now


@dataclass(frozen=True)
class VehicleProgression:
    id: str
    name: str
    slug: str
    unlock_level: int
    unlock_xp: int
    coin_price: int
    model_url: str | None
    thumbnail_url: str | None


VEHICLE_PROGRESSION: tuple[VehicleProgression, ...] = (
    VehicleProgression("skateboard", "Скейтборд", "skateboard", 1, 0, 0, "/assets/models/body/skateboard.glb", "/assets/models/body/skateboard.glb"),
    VehicleProgression("e2f-scooter-yellow", "E2F скутері", "scooter", 2, 200, 300, "/assets/models/body/e2f_scooter_yellow.glb", "/assets/models/body/e2f_scooter_yellow.glb"),
    VehicleProgression("btwin-triban-100-bike", "BTWIN Triban 100 велосипеді", "bicycle", 3, 500, 700, "/assets/models/body/btwin_triban_100_road_bike.glb", "/assets/models/body/btwin_triban_100_road_bike.glb"),
    VehicleProgression("ducati-streetfighter-v4-s", "Ducati Streetfighter V4 S мотоциклі", "motorbike", 4, 900, 1500, "/assets/models/body/2024_ducati_streetfighter_v4_s.glb", "/assets/models/body/2024_ducati_streetfighter_v4_s.glb"),
    VehicleProgression("suzuki-quadzilla-500", "Suzuki Quadzilla 500 квадроциклі", "quad-bike", 5, 1500, 3000, "/assets/models/body/suzuki_quadzilla_500.glb", "/assets/models/body/suzuki_quadzilla_500.glb"),
    VehicleProgression("mini-car-low-poly-v02", "Mini Car Low Poly", "city-car", 6, 2400, 5000, "/assets/models/body/mini_car_low_poly_v02.glb", "/assets/models/body/mini_car_low_poly_v02.glb"),
    VehicleProgression("ford-mustang-shelby-cobra-gt500", "Ford Mustang Shelby Cobra GT500", "suv", 7, 3500, 8000, "/assets/models/body/1967_ford_mustang_shelby_cobra_gt500.glb", "/assets/models/body/1967_ford_mustang_shelby_cobra_gt500.glb"),
    VehicleProgression("jaguar-project-7", "Project 7 көлігі", "sports-car", 8, 5000, 12000, "/assets/models/body/jaguar-project-7.glb", "/car.webp"),
    VehicleProgression("mclaren-720s-spider", "McLaren 720S Spider", "supercar", 9, 7000, 18000, "/assets/models/body/mclaren_720s_spider.glb", "/assets/models/body/mclaren_720s_spider.glb"),
    VehicleProgression("porsche-963-lmdh-hypercar", "Porsche 963 LMDh", "hypercar", 10, 10000, 30000, "/assets/models/body/porsche_963_lmdh_hypercar.glb", "/assets/models/body/porsche_963_lmdh_hypercar.glb"),
)

XP_PER_CORRECT = 10
COINS_BY_DIFFICULTY = {"easy": 5, "medium": 8, "hard": 12}
COMBO_BONUSES = {5: 20, 10: 50, 20: 150}


class GamificationService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    @staticmethod
    def next_level_xp(level: int) -> int:
        for item in VEHICLE_PROGRESSION:
            if item.unlock_level > level:
                return item.unlock_xp
        return VEHICLE_PROGRESSION[-1].unlock_xp

    async def get_or_create_state(self, student_id: uuid.UUID) -> StudentGamification:
        state = await self.session.get(StudentGamification, student_id)
        if state is None:
            state = StudentGamification(student_id=student_id)
            self.session.add(state)
            await self.session.flush()
            await self._ensure_catalog()
            await self._ensure_default_vehicle(student_id)
        return state

    async def get_me(self, student_id: uuid.UUID) -> dict[str, Any]:
        state = await self.get_or_create_state(student_id)
        await self._ensure_catalog()
        await self._ensure_default_vehicle(student_id)
        owned_ids = set(await self._owned_vehicle_ids(student_id))
        selected_vehicle = await self._selected_vehicle_id(student_id)

        vehicles = [self._vehicle_payload(item, state, owned_ids, selected_vehicle) for item in VEHICLE_PROGRESSION]
        return {
            "level": state.level,
            "xp": state.xp,
            "coins": state.coins,
            "combo_streak": state.combo_streak,
            "daily_streak": state.daily_streak,
            "total_problems_solved": state.total_problems_solved,
            "next_level_xp": self.next_level_xp(state.level),
            "owned_vehicles": list(owned_ids),
            "selected_vehicle": selected_vehicle,
            "vehicles": vehicles,
            "shop_items": await self._garage_item_payloads(student_id),
        }

    async def answer_result(self, student_id: uuid.UUID, *, correct: bool, difficulty: str) -> dict[str, Any]:
        state = await self.get_or_create_state(student_id)
        await self._ensure_catalog()

        previous_level = state.level
        previous_unlocked = self._unlocked_vehicle_ids(state.level, state.xp)
        difficulty_key = normalize_difficulty(difficulty)
        xp_gained = XP_PER_CORRECT if correct else 0
        base_coins = COINS_BY_DIFFICULTY[difficulty_key] if correct else 0
        combo_bonus = 0

        if correct:
            state.xp += xp_gained
            state.coins += base_coins
            state.combo_streak += 1
            state.total_problems_solved += 1
            combo_bonus = COMBO_BONUSES.get(state.combo_streak, 0)
            if combo_bonus:
                state.coins += combo_bonus
            self._update_daily_streak(state)
        else:
            state.combo_streak = 0

        state.level = level_for_xp(state.xp)
        new_unlocked = self._unlocked_vehicle_ids(state.level, state.xp) - previous_unlocked
        await self.session.flush()

        return {
            "xp_gained": xp_gained,
            "coins_gained": base_coins + combo_bonus,
            "base_coins": base_coins,
            "combo_bonus": combo_bonus,
            "combo_streak": state.combo_streak,
            "daily_streak": state.daily_streak,
            "new_level": state.level,
            "level_up": state.level > previous_level,
            "unlocked_vehicle": self._vehicle_by_id(next(iter(new_unlocked), "")),
        }

    async def award_practice_answer(self, user_id: uuid.UUID, is_correct: bool, current_streak: int) -> tuple[int, int]:
        result = await self.answer_result(user_id, correct=is_correct, difficulty="medium")
        return int(result["xp_gained"]), int(result["coins_gained"])

    async def get_profile(self, user_id: uuid.UUID) -> dict[str, Any]:
        return await self.get_me(user_id)

    async def buy_vehicle(self, student_id: uuid.UUID, vehicle_id: str) -> dict[str, Any]:
        state = await self.get_or_create_state(student_id)
        await self._ensure_catalog()
        vehicle = await self._vehicle_row(vehicle_id)
        if vehicle is None:
            raise AppError(status_code=404, code="not_found", message="Vehicle not found")
        if await self._owns_vehicle(student_id, vehicle.id):
            raise AppError(status_code=409, code="already_owned", message="Vehicle already owned")
        if state.level < vehicle.unlock_level or state.xp < vehicle.unlock_xp:
            raise AppError(status_code=403, code="locked", message="Vehicle is still locked")
        if state.coins < vehicle.coin_price:
            raise AppError(status_code=400, code="not_enough_coins", message="Not enough coins")

        state.coins -= vehicle.coin_price
        self.session.add(StudentVehicle(student_id=student_id, vehicle_id=vehicle.id, is_selected=False))
        await self.session.flush()
        return await self.get_me(student_id)

    async def select_vehicle(self, student_id: uuid.UUID, vehicle_id: str) -> dict[str, Any]:
        await self.get_or_create_state(student_id)
        if not await self._owns_vehicle(student_id, vehicle_id):
            raise AppError(status_code=403, code="not_owned", message="Buy this vehicle before selecting it")
        await self.session.execute(update(StudentVehicle).where(StudentVehicle.student_id == student_id).values(is_selected=False))
        result = await self.session.execute(
            select(StudentVehicle).where(StudentVehicle.student_id == student_id, StudentVehicle.vehicle_id == vehicle_id)
        )
        row = result.scalar_one()
        row.is_selected = True
        await self.session.flush()
        return await self.get_me(student_id)

    async def buy_item(self, student_id: uuid.UUID, item_id: str) -> dict[str, Any]:
        state = await self.get_or_create_state(student_id)
        item = await self.session.get(GarageItem, item_id)
        if item is None or not item.is_active:
            raise AppError(status_code=404, code="not_found", message="Garage item not found")
        if state.level < item.unlock_level:
            raise AppError(status_code=403, code="locked", message="Garage item is still locked")
        if await self._owns_item(student_id, item.id):
            raise AppError(status_code=409, code="already_owned", message="Garage item already owned")
        if state.coins < item.coin_price:
            raise AppError(status_code=400, code="not_enough_coins", message="Not enough coins")
        state.coins -= item.coin_price
        self.session.add(StudentGarageItem(student_id=student_id, garage_item_id=item.id))
        await self.session.flush()
        return await self.get_me(student_id)

    async def equip_item(self, student_id: uuid.UUID, *, vehicle_id: str, item_type: str, item_id: str | None) -> dict[str, Any]:
        if not await self._owns_vehicle(student_id, vehicle_id):
            raise AppError(status_code=403, code="not_owned", message="Buy this vehicle before customizing it")
        if item_id and not await self._owns_item(student_id, item_id):
            raise AppError(status_code=403, code="item_not_owned", message="Buy this item before equipping it")

        result = await self.session.execute(
            select(SelectedVehicleCustomization).where(
                SelectedVehicleCustomization.student_id == student_id,
                SelectedVehicleCustomization.vehicle_id == vehicle_id,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = SelectedVehicleCustomization(student_id=student_id, vehicle_id=vehicle_id)
            self.session.add(row)

        field = f"{item_type}_item_id"
        if field not in {"wheel_item_id", "paint_item_id", "roof_item_id", "spoiler_item_id", "headlight_item_id", "sticker_item_id"}:
            raise AppError(status_code=400, code="validation_error", message="Unsupported garage item type")
        setattr(row, field, item_id)
        await self.session.flush()
        return await self.get_me(student_id)

    async def _ensure_catalog(self) -> None:
        for item in VEHICLE_PROGRESSION:
            row = await self.session.get(Vehicle, item.id)
            if row is None:
                self.session.add(
                    Vehicle(
                        id=item.id,
                        name=item.name,
                        slug=item.slug,
                        unlock_level=item.unlock_level,
                        unlock_xp=item.unlock_xp,
                        coin_price=item.coin_price,
                        model_url=item.model_url,
                        thumbnail_url=item.thumbnail_url,
                    )
                )

        for item in default_garage_items():
            row = await self.session.get(GarageItem, item["id"])
            if row is None:
                self.session.add(GarageItem(**item))
        await self.session.flush()

    async def _ensure_default_vehicle(self, student_id: uuid.UUID) -> None:
        if not await self._owns_vehicle(student_id, "skateboard"):
            self.session.add(StudentVehicle(student_id=student_id, vehicle_id="skateboard", is_selected=True))
            await self.session.flush()

    def _update_daily_streak(self, state: StudentGamification) -> None:
        today = utc_now().date()
        if state.last_streak_date == today:
            return
        if state.last_streak_date == today - timedelta(days=1):
            state.daily_streak += 1
        else:
            state.daily_streak = 1
        state.last_streak_date = today

    async def _owned_vehicle_ids(self, student_id: uuid.UUID) -> list[str]:
        result = await self.session.execute(select(StudentVehicle.vehicle_id).where(StudentVehicle.student_id == student_id))
        return list(result.scalars().all())

    async def _selected_vehicle_id(self, student_id: uuid.UUID) -> str:
        result = await self.session.execute(
            select(StudentVehicle.vehicle_id).where(StudentVehicle.student_id == student_id, StudentVehicle.is_selected.is_(True))
        )
        return result.scalar_one_or_none() or "skateboard"

    async def _owns_vehicle(self, student_id: uuid.UUID, vehicle_id: str) -> bool:
        result = await self.session.execute(
            select(StudentVehicle.id).where(StudentVehicle.student_id == student_id, StudentVehicle.vehicle_id == vehicle_id)
        )
        return result.scalar_one_or_none() is not None

    async def _owns_item(self, student_id: uuid.UUID, item_id: str) -> bool:
        item = await self.session.get(GarageItem, item_id)
        if item is not None and item.coin_price == 0:
            return True
        result = await self.session.execute(
            select(StudentGarageItem.id).where(StudentGarageItem.student_id == student_id, StudentGarageItem.garage_item_id == item_id)
        )
        return result.scalar_one_or_none() is not None

    async def _vehicle_row(self, vehicle_id: str) -> Vehicle | None:
        return await self.session.get(Vehicle, vehicle_id)

    def _vehicle_by_id(self, vehicle_id: str) -> dict[str, Any] | None:
        for item in VEHICLE_PROGRESSION:
            if item.id == vehicle_id:
                return item.__dict__
        return None

    def _unlocked_vehicle_ids(self, level: int, xp: int) -> set[str]:
        return {item.id for item in VEHICLE_PROGRESSION if level >= item.unlock_level and xp >= item.unlock_xp}

    def _vehicle_payload(
        self,
        item: VehicleProgression,
        state: StudentGamification,
        owned_ids: set[str],
        selected_vehicle: str,
    ) -> dict[str, Any]:
        is_unlocked = state.level >= item.unlock_level and state.xp >= item.unlock_xp
        return {
            "id": item.id,
            "name": item.name,
            "slug": item.slug,
            "unlock_level": item.unlock_level,
            "unlock_xp": item.unlock_xp,
            "coin_price": item.coin_price,
            "model_url": item.model_url,
            "thumbnail_url": item.thumbnail_url,
            "is_unlocked": is_unlocked,
            "is_owned": item.id in owned_ids,
            "is_selected": item.id == selected_vehicle,
        }

    async def _garage_item_payloads(self, student_id: uuid.UUID) -> list[dict[str, Any]]:
        owned = {
            item_id
            for item_id in (
                await self.session.execute(
                    select(StudentGarageItem.garage_item_id).where(StudentGarageItem.student_id == student_id)
                )
            ).scalars()
        }
        result = await self.session.execute(select(GarageItem).where(GarageItem.is_active.is_(True)))
        return [
            {
                "id": item.id,
                "vehicle_type": item.vehicle_type,
                "item_type": item.item_type,
                "name": item.name,
                "slug": item.slug,
                "coin_price": item.coin_price,
                "unlock_level": item.unlock_level,
                "model_url": item.model_url,
                "thumbnail_url": item.thumbnail_url,
                "rarity": item.rarity,
                "is_owned": item.id in owned or item.coin_price == 0,
            }
            for item in result.scalars().all()
        ]


def level_for_xp(xp: int) -> int:
    level = 1
    for item in VEHICLE_PROGRESSION:
        if xp >= item.unlock_xp:
            level = max(level, item.unlock_level)
    return level


def normalize_difficulty(difficulty: str) -> str:
    value = (difficulty or "medium").lower()
    if value in {"easy", "medium", "hard"}:
        return value
    if value in {"1", "2"}:
        return "easy"
    if value in {"3", "4"}:
        return "medium"
    return "hard"


def difficulty_from_question_level(level: int | None) -> str:
    value = int(level or 1)
    if value <= 2:
        return "easy"
    if value <= 4:
        return "medium"
    return "hard"


def default_garage_items() -> list[dict[str, Any]]:
    return [
        {"id": "paint-original", "vehicle_type": "all", "item_type": "paint", "name": "Бастапқы бояу", "slug": "paint-original", "coin_price": 0, "unlock_level": 1, "rarity": "common"},
        {"id": "paint-blue", "vehicle_type": "all", "item_type": "paint", "name": "Оқу көгі", "slug": "paint-blue", "coin_price": 120, "unlock_level": 1, "rarity": "common"},
        {"id": "paint-red", "vehicle_type": "all", "item_type": "paint", "name": "Жарыс қызылы", "slug": "paint-red", "coin_price": 180, "unlock_level": 2, "rarity": "rare"},
        {"id": "wheel-ice", "vehicle_type": "all", "item_type": "wheel", "name": "Мұз дискі", "slug": "wheel-ice", "coin_price": 0, "unlock_level": 1, "rarity": "common"},
        {"id": "wheel-gold", "vehicle_type": "all", "item_type": "wheel", "name": "Алтын диск", "slug": "wheel-gold", "coin_price": 450, "unlock_level": 4, "rarity": "epic"},
        {"id": "sticker-black", "vehicle_type": "all", "item_type": "sticker", "name": "Карбон стикер", "slug": "sticker-black", "coin_price": 0, "unlock_level": 1, "rarity": "common"},
        {"id": "sticker-blue", "vehicle_type": "all", "item_type": "sticker", "name": "Электр көк стикер", "slug": "sticker-blue", "coin_price": 260, "unlock_level": 3, "rarity": "rare"},
        {"id": "roof-carbon", "vehicle_type": "car", "item_type": "roof", "name": "Карбон шатыр", "slug": "roof-carbon", "coin_price": 600, "unlock_level": 6, "rarity": "epic"},
        {"id": "spoiler-track", "vehicle_type": "car", "item_type": "spoiler", "name": "Трек спойлері", "slug": "spoiler-track", "coin_price": 900, "unlock_level": 8, "rarity": "epic"},
        {"id": "headlight-led", "vehicle_type": "car", "item_type": "headlight", "name": "LED жарық", "slug": "headlight-led", "coin_price": 500, "unlock_level": 5, "rarity": "rare"},
    ]

