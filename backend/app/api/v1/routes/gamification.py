from __future__ import annotations

from typing import Any

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


class EquipItemRequest(BaseModel):
    vehicle_id: str
    item_type: str
    item_id: str | None = None


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


@router.post("/answer-result")
async def post_answer_result(
    payload: AnswerResultRequest,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    reward = await svc.answer_result(user.id, correct=payload.correct, difficulty=payload.difficulty)
    return {"data": reward}


@router.get("/shop")
async def get_shop_items(
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(),
):
    profile = await svc.get_me(user.id)
    return {"data": profile["shop_items"]}


@router.post("/garage/buy-vehicle/{vehicle_id}")
async def buy_vehicle(
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
