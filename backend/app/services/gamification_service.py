from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.session import get_db_session
from app.models.gamification import (
    GarageItem,
    LevelReward,
    OwnedVehicle,
    RewardEvent,
    SelectedVehicleCustomization,
    StudentGamification,
    StudentGarageItem,
    StudentStreak,
    StudentVehicle,
    StudentWallet,
    StreakReward,
    ShopItem,
    TopicReward,
    UserItem,
    Vehicle,
    WalletTransaction,
)
from app.models.enums import GameType
from app.models.notification import Notification
from app.models.profile import StudentProfile
from app.utils.time import utc_now


CHARACTER_PRESET_LEVELS = {
    "default-boy": 1, "default-girl": 1, "glover": 3, "hana": 4, "kenji": 5,
    "jayda": 6, "zell": 7, "myriad": 9, "jackal": 12,
}
CHARACTER_LEVEL_RANGES = {
    "body": (1, 1), "head": (1, 1), "eyes": (1, 1),
    "hairFront": (1, 12), "hairBack": (1, 12), "top": (1, 12), "bottom": (1, 12), "feet": (1, 12),
    "eyeBrows": (2, 5), "eyeLashes": (2, 5), "pupil": (2, 5), "eyeShine": (2, 5),
    "socks": (3, 9), "gloves": (3, 9), "leggings": (4, 8),
    "headAcc": (5, 10), "upperFace": (5, 10), "lowerFace": (5, 10), "neck": (5, 10), "faceDetails": (5, 10),
    "overall": (6, 12), "makeUpCheeks": (7, 10), "makeUpLips": (7, 10),
    "underLower": (1, 3), "underUpper": (1, 3),
}
FREE_CHARACTER_ITEMS = {
    "default-boy", "default-girl", "Body_BasicBody", "Head_Young", "Eyes_Eyes01",
    "Brows_BasicBrows", "Eyelashes_LongLashes", "HairFront_ShotaFringe",
    "HairBack_MessyHair", "Top_TankTop", "Bottom_SimpleShorts",
}
# Keep character rewards on the same level-price curve as Garage vehicles.
CHARACTER_BASE_PRICE = [0, 100, 250, 500, 900, 1400, 2100, 3000, 4200, 6000, 8500, 11000, 13500]


def character_item_progression(item_key: str, category: str) -> tuple[int, int]:
    if category not in CHARACTER_LEVEL_RANGES and category != "characters":
        raise AppError(status_code=400, code="invalid_category", message="Unknown BoZo category")
    item_hash = sum(ord(character) * (index + 1) for index, character in enumerate(item_key))
    if category == "characters":
        if item_key not in CHARACTER_PRESET_LEVELS:
            raise AppError(status_code=400, code="invalid_item", message="Unknown BoZo preset")
        level = CHARACTER_PRESET_LEVELS[item_key]
    else:
        minimum, maximum = CHARACTER_LEVEL_RANGES[category]
        level = minimum + item_hash % (maximum - minimum + 1)
    price = 0 if item_key in FREE_CHARACTER_ITEMS else CHARACTER_BASE_PRICE[level]
    return level, price


@dataclass(frozen=True)
class VehicleProgression:
    id: str
    name: str
    slug: str
    vehicle_type: str
    level_required: int
    xp_required: int
    price: int
    model_url: str | None
    thumbnail_url: str | None


VEHICLE_PROGRESSION: tuple[VehicleProgression, ...] = (
    VehicleProgression("skateboard", "Скейтборд", "skateboard", "skateboard", 1, 0, 100, "/assets/models/body/skateboard.glb", "/assets/models/body/skateboard.glb"),
    VehicleProgression("e2f-scooter-yellow", "Скутер", "scooter", "scooter", 2, 300, 250, "/assets/models/body/e2f_scooter_yellow.glb", "/assets/models/body/e2f_scooter_yellow.glb"),
    VehicleProgression("btwin-triban-100-bike", "Велосипед", "bike", "bike", 3, 700, 500, "/assets/models/body/btwin_triban_100_road_bike.glb", "/assets/models/body/btwin_triban_100_road_bike.glb"),
    VehicleProgression("vino", "Vino көлігі", "vino", "car", 4, 1200, 900, "/assets/models/body/vino.glb", "/assets/models/body/vino.glb"),
    VehicleProgression("free-concept-sport-bike", "Спорт мотоцикл", "concept-sport-bike", "motorbike", 5, 1800, 1400, "/assets/models/body/free_concept_sport_bike.glb", "/assets/models/body/free_concept_sport_bike.glb"),
    VehicleProgression("ducati-streetfighter-v4-s", "Мотоцикл", "motorbike", "motorbike", 6, 2500, 2100, "/assets/models/body/2024_ducati_streetfighter_v4_s.glb", "/assets/models/body/2024_ducati_streetfighter_v4_s.glb"),
    VehicleProgression("suzuki-quadzilla-500", "Квадроцикл", "quad-bike", "quad-bike", 7, 3300, 3000, "/assets/models/body/suzuki_quadzilla_500.glb", "/assets/models/body/suzuki_quadzilla_500.glb"),
    VehicleProgression("mini-car-low-poly-v02", "Шағын көлік", "small-car", "small-car", 8, 4300, 4200, "/assets/models/body/mini_car_low_poly_v02.glb", "/assets/models/body/mini_car_low_poly_v02.glb"),
    VehicleProgression("ford-mustang-shelby-cobra-gt500", "Көлік", "car", "car", 9, 5500, 6000, "/assets/models/body/1967_ford_mustang_shelby_cobra_gt500.glb", "/assets/models/body/1967_ford_mustang_shelby_cobra_gt500.glb"),
    VehicleProgression("jaguar-project-7", "Спорт көлік", "sport-car", "sport-car", 10, 7000, 8500, "/assets/models/body/jaguar-project-7.glb", "/assets/models/body/jaguar-project-7.glb"),
    VehicleProgression("mclaren-720s-spider", "Суперкөлік", "supercar", "supercar", 11, 8800, 11000, "/assets/models/body/mclaren_720s_spider.glb", "/assets/models/body/mclaren_720s_spider.glb"),
    VehicleProgression("porsche-963-lmdh-hypercar", "Гиперкөлік", "hypercar", "hypercar", 12, 10900, 13500, "/assets/models/body/porsche_963_lmdh_hypercar.glb", "/assets/models/body/porsche_963_lmdh_hypercar.glb"),
)

XP_PER_CORRECT = 2
LEVEL_THRESHOLDS: dict[int, int] = {
    1: 0,
    2: 300,
    3: 700,
    4: 1200,
    5: 1800,
    6: 2500,
    7: 3300,
    8: 4300,
    9: 5500,
    10: 7000,
    11: 8800,
    12: 10900,
}
SMARTSCORE_MILESTONE_REWARDS: dict[int, int] = {20: 5, 40: 5, 60: 10, 80: 10, 100: 20}
STREAK_REWARD_DAYS = 7
STREAK_REWARD_COINS = 50
LEVEL_REWARD_COINS = 100


class GamificationService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    @staticmethod
    def next_level_xp(level: int) -> int:
        for next_level in sorted(LEVEL_THRESHOLDS):
            if next_level > level:
                return LEVEL_THRESHOLDS[next_level]
        return LEVEL_THRESHOLDS[max(LEVEL_THRESHOLDS)]

    async def get_or_create_wallet(self, student_id: uuid.UUID) -> StudentWallet:
        await self._ensure_catalog()
        wallet = await self.session.get(StudentWallet, student_id)
        if wallet is None:
            legacy = await self.session.get(StudentGamification, student_id)
            wallet = StudentWallet(
                student_id=student_id,
                coins=int(legacy.coins or 0) if legacy else 0,
                xp=int(legacy.xp or 0) if legacy else 0,
                level=level_for_xp(int(legacy.xp or 0)) if legacy else 1,
                total_problems_solved=int(legacy.total_problems_solved or 0) if legacy else 0,
            )
            self.session.add(wallet)
            await self.session.flush()
        wallet.level = level_for_xp(wallet.xp)
        await self._ensure_default_vehicle(student_id, wallet)
        return wallet

    async def get_or_create_state(self, student_id: uuid.UUID) -> StudentGamification:
        state = await self.session.get(StudentGamification, student_id)
        if state is None:
            state = StudentGamification(student_id=student_id)
            self.session.add(state)
            await self.session.flush()
        return state

    async def get_or_create_streak(self, student_id: uuid.UUID) -> StudentStreak:
        streak = await self.session.get(StudentStreak, student_id)
        if streak is None:
            legacy = await self.session.get(StudentGamification, student_id)
            streak = StudentStreak(
                student_id=student_id,
                current_streak=int(legacy.daily_streak or 0) if legacy else 0,
                longest_streak=int(legacy.daily_streak or 0) if legacy else 0,
                last_active_date=legacy.last_streak_date if legacy else None,
                streak_started_at=self._streak_start_date(
                    legacy.last_streak_date,
                    int(legacy.daily_streak or 0),
                )
                if legacy and legacy.last_streak_date
                else None,
                streak_sequence_id=self._streak_sequence_id(student_id, legacy.last_streak_date)
                if legacy and legacy.last_streak_date and int(legacy.daily_streak or 0) > 0
                else None,
                last_7_day_reward_cycle=0,
            )
            self.session.add(streak)
            await self.session.flush()
        return streak

    async def get_me(self, student_id: uuid.UUID) -> dict[str, Any]:
        wallet = await self.get_or_create_wallet(student_id)
        streak = await self.get_or_create_streak(student_id)
        owned_ids = set(await self._owned_vehicle_ids(student_id))
        selected_vehicle = wallet.active_vehicle_id or await self._selected_vehicle_id(student_id)
        vehicles = [self._vehicle_payload(item, wallet, owned_ids, selected_vehicle) for item in VEHICLE_PROGRESSION]
        active_vehicle = next((vehicle for vehicle in vehicles if vehicle["id"] == selected_vehicle), None)
        return {
            "level": wallet.level,
            "xp": wallet.xp,
            "coins": wallet.coins,
            "combo_streak": 0,
            "daily_streak": streak.current_streak,
            "streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "total_problems_solved": wallet.total_problems_solved,
            "next_level_xp": self.next_level_xp(wallet.level),
            "xp_to_next_level": max(0, self.next_level_xp(wallet.level) - wallet.xp),
            "smartscore_milestones": [
                {"milestone": milestone, "coins": coins}
                for milestone, coins in SMARTSCORE_MILESTONE_REWARDS.items()
            ],
            "owned_vehicles": list(owned_ids),
            "selected_vehicle": selected_vehicle,
            "active_vehicle": active_vehicle,
            "vehicles": vehicles,
            "shop_items": await self._garage_item_payloads(student_id),
        }

    async def get_wallet(self, student_id: uuid.UUID) -> dict[str, Any]:
        profile = await self.get_me(student_id)
        return {
            "coins": profile["coins"],
            "xp": profile["xp"],
            "level": profile["level"],
            "streak": profile["streak"],
            "active_vehicle": profile["active_vehicle"],
        }

    async def _active_game(self, student_id: uuid.UUID) -> GameType:
        game = (await self.session.execute(
            select(StudentProfile.active_game).where(StudentProfile.user_id == student_id)
        )).scalar_one_or_none()
        if game is None:
            raise AppError(status_code=409, code="game_not_selected", message="Choose a game first.")
        return game

    async def require_game(self, student_id: uuid.UUID, expected: GameType) -> None:
        if await self._active_game(student_id) != expected:
            raise AppError(status_code=403, code="inactive_game", message=f"Switch to {expected.value} to use this customization.")

    async def get_active_shop(self, student_id: uuid.UUID) -> list[dict[str, Any]]:
        game = await self._active_game(student_id)
        wallet = await self.get_or_create_wallet(student_id)
        if game == GameType.CAR:
            return await self._garage_item_payloads(student_id)

        owned_result = await self.session.execute(select(UserItem).where(UserItem.user_id == student_id))
        owned = {row.item_id: row for row in owned_result.scalars().all()}
        items_result = await self.session.execute(
            select(ShopItem).where(ShopItem.game_type == game).order_by(ShopItem.required_level, ShopItem.name)
        )
        return [
            {
                "id": str(item.id),
                "name": item.name,
                "game_type": item.game_type.value,
                "category": item.category,
                "price": item.cost,
                "required_level": item.required_level,
                "rarity": item.rarity,
                "asset_url": item.asset_url,
                "owned": item.id in owned,
                "equipped": bool(owned.get(item.id) and owned[item.id].is_equipped),
                "locked": wallet.level < item.required_level,
            }
            for item in items_result.scalars().all()
        ]

    async def get_inventories(self, student_id: uuid.UUID) -> dict[str, list[str]]:
        garage_rows = await self.session.execute(
            select(StudentGarageItem.garage_item_id).where(StudentGarageItem.student_id == student_id)
        )
        character_rows = await self.session.execute(
            select(ShopItem.asset_url).join(UserItem, ShopItem.id == UserItem.item_id).where(
                UserItem.user_id == student_id, ShopItem.game_type == GameType.CHARACTER
            )
        )
        return {
            "car_inventory": list(garage_rows.scalars().all()),
            "character_inventory": [
                value.removeprefix("bozo:") for value in character_rows.scalars().all()
                if value and value.startswith("bozo:")
            ],
        }

    async def buy_character_asset(
        self,
        student_id: uuid.UUID,
        *,
        item_key: str,
        name: str,
        category: str,
        asset_url: str | None,
    ) -> dict[str, Any]:
        await self.require_game(student_id, GameType.CHARACTER)
        level, price = character_item_progression(item_key, category)
        wallet = await self.get_or_create_wallet(student_id)
        item_id = uuid.uuid5(uuid.NAMESPACE_URL, f"studypoint:bozo:{item_key}")
        item = await self.session.get(ShopItem, item_id)
        if item is None:
            item = ShopItem(
                id=item_id,
                name=name,
                type=category,
                category=category,
                cost=price,
                required_level=level,
                rarity="legendary" if level == 12 else "rare" if level >= 8 else "common",
                game_type=GameType.CHARACTER,
                asset_url=f"bozo:{item_key}",
            )
            self.session.add(item)
            await self.session.flush()
        exists = (await self.session.execute(
            select(UserItem.id).where(UserItem.user_id == student_id, UserItem.item_id == item_id)
        )).scalar_one_or_none()
        if exists is not None:
            raise AppError(status_code=409, code="already_owned", message="Бұл зат бұрын сатып алынған")
        if wallet.level < level:
            raise AppError(status_code=403, code="locked", message=f"Бұл зат үшін {level}-деңгейге жет")
        if wallet.coins < price:
            raise AppError(status_code=400, code="not_enough_coins", message=f"Тағы {price - wallet.coins} монета керек")
        wallet.coins -= price
        self.session.add(UserItem(user_id=student_id, item_id=item_id))
        self._add_wallet_transaction(
            student_id,
            transaction_type="CHARACTER_PURCHASE",
            xp_change=0,
            coin_change=-price,
            wallet=wallet,
            reference_type="bozo_item",
            reference_id=item_key,
            metadata={"item_key": item_key, "name": name, "category": category, "source_asset": asset_url},
        )
        legacy = await self.get_or_create_state(student_id)
        legacy.coins = wallet.coins
        await self.session.flush()
        return {"item_key": item_key, "coins": wallet.coins, "owned": True}

    async def buy_character_item(self, student_id: uuid.UUID, item_id: uuid.UUID) -> dict[str, Any]:
        await self.require_game(student_id, GameType.CHARACTER)
        await self.get_or_create_wallet(student_id)
        wallet = (await self.session.execute(
            select(StudentWallet).where(StudentWallet.student_id == student_id).with_for_update()
        )).scalar_one()
        item = await self.session.get(ShopItem, item_id)
        if item is None or item.game_type != GameType.CHARACTER:
            raise AppError(status_code=404, code="not_found", message="Character item not found")
        exists = (await self.session.execute(
            select(UserItem.id).where(UserItem.user_id == student_id, UserItem.item_id == item.id)
        )).scalar_one_or_none()
        if exists is not None:
            raise AppError(status_code=409, code="already_owned", message="Item already owned")
        if wallet.level < item.required_level:
            raise AppError(status_code=403, code="locked", message=f"Reach level {item.required_level}")
        if wallet.coins < item.cost:
            raise AppError(status_code=400, code="not_enough_coins", message="Not enough coins")
        wallet.coins -= item.cost
        legacy = await self.get_or_create_state(student_id)
        legacy.coins = wallet.coins
        self.session.add(UserItem(user_id=student_id, item_id=item.id))
        self._add_wallet_transaction(
            student_id, transaction_type="CHARACTER_PURCHASE", xp_change=0, coin_change=-item.cost,
            wallet=wallet, reference_type="character_item", reference_id=str(item.id),
            metadata={"item_id": str(item.id), "item_name": item.name},
        )
        await self.session.flush()
        return {"item_id": str(item.id), "coins": wallet.coins, "owned": True}

    async def get_vehicles(self, student_id: uuid.UUID) -> list[dict[str, Any]]:
        return (await self.get_me(student_id))["vehicles"]

    async def question_result(
        self,
        student_id: uuid.UUID,
        *,
        correct: bool,
        topic_id: int | None,
        smartscore_before: int,
        smartscore_after: int,
        idempotency_key: str | None = None,
        reference_type: str | None = None,
        reference_id: str | None = None,
    ) -> dict[str, Any]:
        return await self.process_answer_rewards(
            student_id,
            correct=correct,
            topic_id=topic_id,
            smartscore_before=smartscore_before,
            smartscore_after=smartscore_after,
            idempotency_key=idempotency_key,
            reference_type=reference_type,
            reference_id=reference_id,
        )

    async def process_answer_rewards(
        self,
        student_id: uuid.UUID,
        *,
        correct: bool,
        topic_id: int | None,
        smartscore_before: int,
        smartscore_after: int,
        idempotency_key: str | None,
        reference_type: str | None = None,
        reference_id: str | None = None,
    ) -> dict[str, Any]:
        if idempotency_key:
            existing = (
                await self.session.execute(
                    select(RewardEvent).where(
                        RewardEvent.student_id == student_id,
                        RewardEvent.idempotency_key == idempotency_key,
                    )
                )
            ).scalar_one_or_none()
            if existing is not None:
                result = dict(existing.result or {})
                result["idempotent_replay"] = True
                return result

        wallet = await self.get_or_create_wallet(student_id)
        state = await self.get_or_create_state(student_id)
        previous_level = wallet.level

        xp_gained = 0
        milestone_coins = 0
        milestone_rewards: list[dict[str, int]] = []
        streak_bonus = 0
        streak_reward_cycles: list[int] = []

        if correct:
            xp_gained = XP_PER_CORRECT
            wallet.xp += xp_gained
            wallet.total_problems_solved += 1
            self._add_wallet_transaction(
                student_id,
                transaction_type="CORRECT_ANSWER_XP",
                xp_change=xp_gained,
                coin_change=0,
                wallet=wallet,
                reference_type=reference_type or "practice_attempt",
                reference_id=reference_id,
                metadata={"topic_id": topic_id},
            )

            if topic_id is not None:
                milestone_coins, milestone_rewards = await self._award_smartscore_milestones(
                    student_id=student_id,
                    topic_id=topic_id,
                    score_before=smartscore_before,
                    score_after=smartscore_after,
                )
                if milestone_coins:
                    wallet.coins += milestone_coins
                    self._add_wallet_transaction(
                        student_id,
                        transaction_type="SMARTSCORE_MILESTONE",
                        xp_change=0,
                        coin_change=milestone_coins,
                        wallet=wallet,
                        reference_type="skill",
                        reference_id=str(topic_id),
                        metadata={"milestones": milestone_rewards, "score_before": smartscore_before, "score_after": smartscore_after},
                    )

            streak_bonus, streak_reward_cycles = await self._update_daily_streak(student_id)

        wallet.level = calculate_level(wallet.xp)
        level_bonus = 0
        rewarded_levels: list[int] = []
        if correct:
            level_bonus, rewarded_levels = await self._award_level_rewards(student_id, wallet, previous_level)

        if streak_bonus:
            wallet.coins += streak_bonus
            self._add_wallet_transaction(
                student_id,
                transaction_type="STREAK_REWARD",
                xp_change=0,
                coin_change=streak_bonus,
                wallet=wallet,
                reference_type="streak",
                reference_id=",".join(str(cycle) for cycle in streak_reward_cycles),
                metadata={"cycles": streak_reward_cycles},
            )

        streak = await self.get_or_create_streak(student_id)
        state.xp = wallet.xp
        state.coins = wallet.coins
        state.level = wallet.level
        state.daily_streak = streak.current_streak
        state.last_streak_date = streak.last_active_date
        state.total_problems_solved = wallet.total_problems_solved
        state.combo_streak = 0

        coins_gained = milestone_coins + level_bonus + streak_bonus
        result = {
            "xp_gained": xp_gained,
            "coins_gained": coins_gained,
            "base_coins": 0,
            "combo_bonus": 0,
            "combo_streak": 0,
            "daily_streak": streak.current_streak,
            "streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "streak_bonus": streak_bonus,
            "streak_reward_cycles": streak_reward_cycles,
            "milestone_coins": milestone_coins,
            "milestone_rewards": milestone_rewards,
            "level_bonus": level_bonus,
            "rewarded_levels": rewarded_levels,
            "new_level": wallet.level,
            "level": wallet.level,
            "level_up": wallet.level > previous_level,
            "unlocked_vehicle": self._first_vehicle_for_level(wallet.level, previous_level),
            "wallet": {
                "xp": wallet.xp,
                "coins": wallet.coins,
                "level": wallet.level,
                "next_level_xp": self.next_level_xp(wallet.level),
                "xp_to_next_level": max(0, self.next_level_xp(wallet.level) - wallet.xp),
            },
        }
        if idempotency_key:
            self.session.add(
                RewardEvent(
                    student_id=student_id,
                    idempotency_key=idempotency_key,
                    reference_type=reference_type,
                    reference_id=reference_id,
                    is_correct=correct,
                    xp_awarded=xp_gained,
                    coins_awarded=coins_gained,
                    result=result,
                )
            )
        await self.session.flush()
        return result

    async def answer_result(self, student_id: uuid.UUID, *, correct: bool, difficulty: str = "medium") -> dict[str, Any]:
        return await self.question_result(
            student_id,
            correct=correct,
            topic_id=None,
            smartscore_before=0,
            smartscore_after=0,
        )

    async def award_practice_answer(
        self,
        user_id: uuid.UUID,
        is_correct: bool,
        current_streak: int,
        *,
        topic_id: int | None = None,
        smartscore_before: int = 0,
        smartscore_after: int = 0,
    ) -> tuple[int, int]:
        result = await self.question_result(
            user_id,
            correct=is_correct,
            topic_id=topic_id,
            smartscore_before=smartscore_before,
            smartscore_after=smartscore_after,
        )
        return int(result["xp_gained"]), int(result["coins_gained"])

    async def get_profile(self, user_id: uuid.UUID) -> dict[str, Any]:
        return await self.get_me(user_id)

    async def buy_vehicle(self, student_id: uuid.UUID, vehicle_id: str) -> dict[str, Any]:
        await self.require_game(student_id, GameType.CAR)
        wallet = await self.get_or_create_wallet(student_id)
        vehicle = await self._vehicle_row(vehicle_id)
        if vehicle is None or not vehicle.is_active:
            raise AppError(status_code=404, code="not_found", message="Vehicle not found")
        if await self._owns_vehicle(student_id, vehicle.id):
            raise AppError(status_code=409, code="already_owned", message="Vehicle already owned")

        level_required = int(vehicle.level_required or vehicle.unlock_level or 1)
        xp_required = int(vehicle.xp_required or vehicle.unlock_xp or 0)
        price = int(vehicle.price or vehicle.coin_price or 0)
        if wallet.level < level_required or wallet.xp < xp_required:
            raise AppError(status_code=403, code="locked", message=f"{vehicle.name} ашу үшін {level_required}-деңгейге жет")
        if wallet.coins < price:
            raise AppError(status_code=400, code="not_enough_coins", message=f"Тағы {price - wallet.coins} монета керек")

        wallet.coins -= price
        self._add_wallet_transaction(
            student_id,
            transaction_type="VEHICLE_PURCHASE",
            xp_change=0,
            coin_change=-price,
            wallet=wallet,
            reference_type="vehicle",
            reference_id=vehicle.id,
            metadata={"vehicle_id": vehicle.id, "vehicle_name": vehicle.name},
        )
        legacy_state = await self.get_or_create_state(student_id)
        legacy_state.coins = wallet.coins
        self.session.add(OwnedVehicle(student_id=student_id, vehicle_id=vehicle.id))
        self.session.add(StudentVehicle(student_id=student_id, vehicle_id=vehicle.id, is_selected=False))
        await self.session.flush()
        return await self.get_me(student_id)

    async def select_vehicle(self, student_id: uuid.UUID, vehicle_id: str) -> dict[str, Any]:
        await self.require_game(student_id, GameType.CAR)
        wallet = await self.get_or_create_wallet(student_id)
        if not await self._owns_vehicle(student_id, vehicle_id):
            raise AppError(status_code=403, code="not_owned", message="Buy this vehicle before selecting it")
        wallet.active_vehicle_id = vehicle_id
        await self.session.execute(update(StudentVehicle).where(StudentVehicle.student_id == student_id).values(is_selected=False))
        result = await self.session.execute(
            select(StudentVehicle).where(StudentVehicle.student_id == student_id, StudentVehicle.vehicle_id == vehicle_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = StudentVehicle(student_id=student_id, vehicle_id=vehicle_id, is_selected=True)
            self.session.add(row)
        else:
            row.is_selected = True
        await self.session.flush()
        return await self.get_me(student_id)

    async def buy_item(self, student_id: uuid.UUID, item_id: str) -> dict[str, Any]:
        await self.require_game(student_id, GameType.CAR)
        wallet = await self.get_or_create_wallet(student_id)
        item = await self.session.get(GarageItem, item_id)
        if item is None or not item.is_active:
            raise AppError(status_code=404, code="not_found", message="Garage item not found")
        if wallet.level < item.unlock_level:
            raise AppError(status_code=403, code="locked", message="Garage item is still locked")
        if await self._owns_item(student_id, item.id):
            raise AppError(status_code=409, code="already_owned", message="Garage item already owned")
        if wallet.coins < item.coin_price:
            raise AppError(status_code=400, code="not_enough_coins", message=f"Тағы {item.coin_price - wallet.coins} монета керек")
        wallet.coins -= item.coin_price
        self._add_wallet_transaction(
            student_id,
            transaction_type="CUSTOMIZATION_PURCHASE",
            xp_change=0,
            coin_change=-int(item.coin_price or 0),
            wallet=wallet,
            reference_type="garage_item",
            reference_id=item.id,
            metadata={"item_id": item.id, "item_type": item.item_type, "item_name": item.name},
        )
        legacy_state = await self.get_or_create_state(student_id)
        legacy_state.coins = wallet.coins
        self.session.add(StudentGarageItem(student_id=student_id, garage_item_id=item.id))
        await self.session.flush()
        return await self.get_me(student_id)

    async def equip_item(self, student_id: uuid.UUID, *, vehicle_id: str, item_type: str, item_id: str | None) -> dict[str, Any]:
        await self.require_game(student_id, GameType.CAR)
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

    async def _award_smartscore_milestones(
        self,
        *,
        student_id: uuid.UUID,
        topic_id: int,
        score_before: int,
        score_after: int,
    ) -> tuple[int, list[dict[str, int]]]:
        result = await self.session.execute(
            select(TopicReward).where(TopicReward.student_id == student_id, TopicReward.topic_id == topic_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = TopicReward(student_id=student_id, topic_id=topic_id, rewarded_milestones=[])
            self.session.add(row)
            await self.session.flush()

        rewarded = {int(value) for value in (row.rewarded_milestones or [])}
        newly_rewarded: list[int] = []
        coins = 0
        for milestone, reward in SMARTSCORE_MILESTONE_REWARDS.items():
            if score_before < milestone <= score_after and milestone not in rewarded:
                newly_rewarded.append(milestone)
                coins += reward

        if newly_rewarded:
            row.rewarded_milestones = sorted(rewarded | set(newly_rewarded))

        return coins, [{"milestone": milestone, "coins": SMARTSCORE_MILESTONE_REWARDS[milestone]} for milestone in newly_rewarded]

    async def _update_daily_streak(self, student_id: uuid.UUID) -> tuple[int, list[int]]:
        streak = await self.get_or_create_streak(student_id)
        today = utc_now().date()
        if streak.last_active_date == today:
            return 0, []
        if streak.last_active_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
            streak.streak_started_at = today
            streak.streak_sequence_id = self._streak_sequence_id(student_id, today)
            streak.last_7_day_reward_cycle = 0
        streak.last_active_date = today
        if streak.streak_started_at is None:
            streak.streak_started_at = self._streak_start_date(today, streak.current_streak)
        if streak.streak_sequence_id is None:
            streak.streak_sequence_id = self._streak_sequence_id(student_id, streak.streak_started_at)
        streak.longest_streak = max(int(streak.longest_streak or 0), int(streak.current_streak or 0))

        current_cycle = streak.current_streak // STREAK_REWARD_DAYS
        if current_cycle > streak.last_7_day_reward_cycle and streak.streak_sequence_id:
            exists = (
                await self.session.execute(
                    select(StreakReward.id).where(
                        StreakReward.student_id == student_id,
                        StreakReward.streak_sequence_id == streak.streak_sequence_id,
                        StreakReward.cycle_number == current_cycle,
                    )
                )
            ).scalar_one_or_none()
            if exists is not None:
                return 0, []
            streak.last_7_day_reward_cycle = current_cycle
            self.session.add(
                StreakReward(
                    student_id=student_id,
                    streak_sequence_id=streak.streak_sequence_id,
                    cycle_number=current_cycle,
                )
            )
            return STREAK_REWARD_COINS, [current_cycle]
        return 0, []

    async def _award_level_rewards(self, student_id: uuid.UUID, wallet: StudentWallet, previous_level: int) -> tuple[int, list[int]]:
        bonus = 0
        rewarded_levels: list[int] = []
        for level in range(max(2, previous_level + 1), wallet.level + 1):
            exists = (
                await self.session.execute(
                    select(LevelReward.id).where(LevelReward.student_id == student_id, LevelReward.level == level)
                )
            ).scalar_one_or_none()
            if exists is not None:
                continue
            self.session.add(LevelReward(student_id=student_id, level=level))
            self.session.add(
                Notification(
                    user_id=student_id,
                    title=f"Жаңа деңгей ашылды: {level}-деңгей!",
                    content=(
                        f"Құттықтаймыз! Сіз {level}-деңгейге жеттіңіз. "
                        f"{LEVEL_REWARD_COINS} монета алдыңыз және жаңа ойын сыйлықтары ашылды."
                    ),
                    is_read=False,
                )
            )
            wallet.coins += LEVEL_REWARD_COINS
            self._add_wallet_transaction(
                student_id,
                transaction_type="LEVEL_UP_REWARD",
                xp_change=0,
                coin_change=LEVEL_REWARD_COINS,
                wallet=wallet,
                reference_type="level",
                reference_id=str(level),
                metadata={"level": level},
            )
            bonus += LEVEL_REWARD_COINS
            rewarded_levels.append(level)
        return bonus, rewarded_levels

    def _add_wallet_transaction(
        self,
        student_id: uuid.UUID,
        *,
        transaction_type: str,
        xp_change: int,
        coin_change: int,
        wallet: StudentWallet,
        reference_type: str | None,
        reference_id: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.session.add(
            WalletTransaction(
                student_id=student_id,
                transaction_type=transaction_type,
                xp_change=xp_change,
                coin_change=coin_change,
                xp_balance_after=wallet.xp,
                coin_balance_after=wallet.coins,
                reference_type=reference_type,
                reference_id=reference_id,
                transaction_metadata=metadata or {},
            )
        )

    def _streak_sequence_id(self, student_id: uuid.UUID, started_at: date | None) -> str:
        value = started_at.isoformat() if started_at else utc_now().date().isoformat()
        return f"{student_id}:{value}"

    def _streak_start_date(self, last_active_date: date | None, current_streak: int) -> date | None:
        if last_active_date is None or current_streak <= 0:
            return None
        return last_active_date - timedelta(days=current_streak - 1)

    async def _ensure_catalog(self) -> None:
        for item in VEHICLE_PROGRESSION:
            row = await self.session.get(Vehicle, item.id)
            if row is None:
                self.session.add(
                    Vehicle(
                        id=item.id,
                        name=item.name,
                        slug=item.slug,
                        unlock_level=item.level_required,
                        unlock_xp=item.xp_required,
                        coin_price=item.price,
                        level_required=item.level_required,
                        xp_required=item.xp_required,
                        price=item.price,
                        type=item.vehicle_type,
                        model_url=item.model_url,
                        thumbnail_url=item.thumbnail_url,
                    )
                )
            else:
                row.name = item.name
                row.slug = item.slug
                row.unlock_level = item.level_required
                row.unlock_xp = item.xp_required
                row.coin_price = item.price
                row.level_required = item.level_required
                row.xp_required = item.xp_required
                row.price = item.price
                row.type = item.vehicle_type
                row.model_url = item.model_url
                row.thumbnail_url = item.thumbnail_url
                row.is_active = True

        for item in default_garage_items():
            row = await self.session.get(GarageItem, item["id"])
            if row is None:
                self.session.add(GarageItem(**item))
        await self.session.flush()

    async def _ensure_default_vehicle(self, student_id: uuid.UUID, wallet: StudentWallet) -> None:
        if not await self._owns_vehicle(student_id, "skateboard"):
            self.session.add(OwnedVehicle(student_id=student_id, vehicle_id="skateboard"))
            self.session.add(StudentVehicle(student_id=student_id, vehicle_id="skateboard", is_selected=True))
        if not wallet.active_vehicle_id:
            wallet.active_vehicle_id = "skateboard"
        await self.session.flush()

    async def _owned_vehicle_ids(self, student_id: uuid.UUID) -> list[str]:
        result = await self.session.execute(select(OwnedVehicle.vehicle_id).where(OwnedVehicle.student_id == student_id))
        owned = set(result.scalars().all())
        if not owned:
            legacy = await self.session.execute(select(StudentVehicle.vehicle_id).where(StudentVehicle.student_id == student_id))
            owned = set(legacy.scalars().all())
        return list(owned)

    async def _selected_vehicle_id(self, student_id: uuid.UUID) -> str:
        result = await self.session.execute(
            select(StudentVehicle.vehicle_id).where(StudentVehicle.student_id == student_id, StudentVehicle.is_selected.is_(True))
        )
        return result.scalar_one_or_none() or "skateboard"

    async def _owns_vehicle(self, student_id: uuid.UUID, vehicle_id: str) -> bool:
        result = await self.session.execute(
            select(OwnedVehicle.id).where(OwnedVehicle.student_id == student_id, OwnedVehicle.vehicle_id == vehicle_id)
        )
        if result.scalar_one_or_none() is not None:
            return True
        legacy = await self.session.execute(
            select(StudentVehicle.id).where(StudentVehicle.student_id == student_id, StudentVehicle.vehicle_id == vehicle_id)
        )
        return legacy.scalar_one_or_none() is not None

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

    def _first_vehicle_for_level(self, level: int, previous_level: int) -> dict[str, Any] | None:
        for item in VEHICLE_PROGRESSION:
            if previous_level < item.level_required <= level:
                return self._vehicle_progression_payload(item)
        return None

    def _vehicle_progression_payload(self, item: VehicleProgression) -> dict[str, Any]:
        return {
            "id": item.id,
            "name": item.name,
            "slug": item.slug,
            "type": item.vehicle_type,
            "unlock_level": item.level_required,
            "level_required": item.level_required,
            "unlock_xp": item.xp_required,
            "xp_required": item.xp_required,
            "coin_price": item.price,
            "price": item.price,
            "model_url": item.model_url,
            "thumbnail_url": item.thumbnail_url,
        }

    def _vehicle_payload(
        self,
        item: VehicleProgression,
        wallet: StudentWallet,
        owned_ids: set[str],
        selected_vehicle: str,
    ) -> dict[str, Any]:
        is_unlocked = wallet.level >= item.level_required and wallet.xp >= item.xp_required
        payload = self._vehicle_progression_payload(item)
        payload.update(
            {
                "is_unlocked": is_unlocked,
                "is_owned": item.id in owned_ids,
                "is_selected": item.id == selected_vehicle,
                "locked_message": None if is_unlocked else f"{item.name} ашу үшін {item.level_required}-деңгейге жет",
                "coins_needed": max(0, item.price - wallet.coins),
            }
        )
        return payload

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


def calculate_level(total_xp: int) -> int:
    level = 1
    for candidate_level, threshold in sorted(LEVEL_THRESHOLDS.items()):
        if total_xp >= threshold:
            level = candidate_level
    return min(level, max(LEVEL_THRESHOLDS))


def level_for_xp(xp: int) -> int:
    return calculate_level(xp)


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
        {"id": "paint-pink", "vehicle_type": "all", "item_type": "paint", "name": "Қызғылт түс", "slug": "paint-pink", "coin_price": 0, "unlock_level": 1, "rarity": "common"},
        {"id": "wheel-ice", "vehicle_type": "all", "item_type": "wheel", "name": "Мұз дискі", "slug": "wheel-ice", "coin_price": 0, "unlock_level": 1, "rarity": "common"},
        {"id": "wheel-gold", "vehicle_type": "all", "item_type": "wheel", "name": "Алтын диск", "slug": "wheel-gold", "coin_price": 450, "unlock_level": 4, "rarity": "epic"},
        {"id": "sticker-black", "vehicle_type": "all", "item_type": "sticker", "name": "Карбон стикер", "slug": "sticker-black", "coin_price": 0, "unlock_level": 1, "rarity": "common"},
        {"id": "sticker-blue", "vehicle_type": "all", "item_type": "sticker", "name": "Электр көк стикер", "slug": "sticker-blue", "coin_price": 260, "unlock_level": 3, "rarity": "rare"},
        {"id": "roof-carbon", "vehicle_type": "car", "item_type": "roof", "name": "Карбон шатыр", "slug": "roof-carbon", "coin_price": 600, "unlock_level": 6, "rarity": "epic"},
        {"id": "spoiler-track", "vehicle_type": "car", "item_type": "spoiler", "name": "Трек спойлері", "slug": "spoiler-track", "coin_price": 900, "unlock_level": 8, "rarity": "epic"},
        {"id": "headlight-led", "vehicle_type": "car", "item_type": "headlight", "name": "LED жарық", "slug": "headlight-led", "coin_price": 500, "unlock_level": 5, "rarity": "rare"},
    ]
