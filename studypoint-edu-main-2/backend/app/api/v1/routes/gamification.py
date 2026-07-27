from __future__ import annotations

from typing import Any
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.deps import get_current_user
from app.models.user import User
from app.services.gamification_service import GamificationService

router = APIRouter()


class AnswerResultRequest(BaseModel):
    question_id: int | str
    correct: bool
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard|1|2|3|4|5)$")
    topic_id: int | None = None
    smartscore_before: int = 0
    smartscore_after: int = 0
    idempotency_key: str | None = None


class EquipItemRequest(BaseModel):
    vehicle_id: str
    item_type: str
    item_id: str | None = None


class CharacterAssetPurchaseRequest(BaseModel):
    item_key: str = Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=80)
    asset_url: str | None = Field(default=None, max_length=255)


@router.get("/me")
async def get_gamification_me(
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.get_me(user.id)}


@router.get("/profile")
async def get_gamification_profile(
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.get_profile(user.id)}


@router.get("/wallet")
async def get_wallet(
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.get_wallet(user.id)}


@router.get("/vehicles")
async def get_vehicles(
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.get_vehicles(user.id)}


@router.post("/answer-result")
async def post_answer_result(
    payload: AnswerResultRequest,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    reward = await svc.question_result(
        user.id,
        correct=payload.correct,
        topic_id=payload.topic_id,
        smartscore_before=payload.smartscore_before,
        smartscore_after=payload.smartscore_after,
        idempotency_key=payload.idempotency_key,
        reference_type="question",
        reference_id=str(payload.question_id),
    )
    return {"data": reward}


@router.post("/reward/question-result")
async def post_reward_question_result(
    payload: AnswerResultRequest,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    reward = await svc.question_result(
        user.id,
        correct=payload.correct,
        topic_id=payload.topic_id,
        smartscore_before=payload.smartscore_before,
        smartscore_after=payload.smartscore_after,
        idempotency_key=payload.idempotency_key,
        reference_type="question",
        reference_id=str(payload.question_id),
    )
    return {"data": reward}


@router.get("/shop")
async def get_shop_items(
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.get_active_shop(user.id)}


@router.get("/inventory")
async def get_game_inventories(user: User = Depends(get_current_user), svc: GamificationService = Depends()):
    return {"data": await svc.get_inventories(user.id)}


@router.post("/shop/character/{item_id}/buy")
async def buy_character_item(item_id: uuid.UUID, user: User = Depends(get_current_user), svc: GamificationService = Depends()):
    return {"data": await svc.buy_character_item(user.id, item_id)}


@router.post("/shop/character-asset/buy")
async def buy_character_asset(
    payload: CharacterAssetPurchaseRequest,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.buy_character_asset(
        user.id,
        item_key=payload.item_key,
        name=payload.name,
        category=payload.category,
        asset_url=payload.asset_url,
    )}


@router.post("/garage/buy-vehicle/{vehicle_id}")
async def buy_vehicle(
    vehicle_id: str,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.buy_vehicle(user.id, vehicle_id)}


@router.post("/vehicles/{vehicle_id}/buy")
async def buy_vehicle_new_path(
    vehicle_id: str,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.buy_vehicle(user.id, vehicle_id)}


@router.post("/garage/select-vehicle/{vehicle_id}")
async def select_vehicle(
    vehicle_id: str,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.select_vehicle(user.id, vehicle_id)}


@router.post("/vehicles/{vehicle_id}/select")
async def select_vehicle_new_path(
    vehicle_id: str,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.select_vehicle(user.id, vehicle_id)}


@router.post("/garage/buy-item/{item_id}")
async def buy_item(
    item_id: str,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.buy_item(user.id, item_id)}


@router.post("/garage/equip-item")
async def equip_item(
    payload: EquipItemRequest,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    return {"data": await svc.equip_item(user.id, vehicle_id=payload.vehicle_id, item_type=payload.item_type, item_id=payload.item_id)}
