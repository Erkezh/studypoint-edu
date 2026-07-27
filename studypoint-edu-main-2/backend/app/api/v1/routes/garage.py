from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_current_user_optional
from app.db.session import get_db_session
from app.models.user import User
from app.schemas.garage import GarageRandomizeRequest, GarageSaveRequest
from app.api.v1.routes.gamification import EquipItemRequest
from app.services.gamification_service import GamificationService
from app.services.garage_service import GarageService

router = APIRouter()


def get_garage_service(session: AsyncSession = Depends(get_db_session)) -> GarageService:
    return GarageService(session)


def get_gamification_service(session: AsyncSession = Depends(get_db_session)) -> GamificationService:
    return GamificationService(session)


@router.get("/config")
async def get_garage_config(svc: GarageService = Depends(get_garage_service)):
    return {"data": svc.get_config()}


@router.get("/parts")
async def get_garage_parts(svc: GarageService = Depends(get_garage_service)):
    return {"data": svc.get_config()["parts"]}


@router.get("/player-car")
async def get_player_car(
    user: User | None = Depends(get_current_user_optional),
    svc: GarageService = Depends(get_garage_service),
):
    if user is None:
        return {"data": svc.get_config()["defaults"]}
    return {"data": await svc.get_player_car(user.id)}


@router.post("/save")
async def save_player_car(
    payload: GarageSaveRequest,
    user: User = Depends(get_current_user),
    svc: GarageService = Depends(get_garage_service),
):
    selection = await svc.save_player_car(user.id, payload.selection)
    return {"data": {"selection": selection}}


@router.post("/randomize")
async def randomize_player_car(
    payload: GarageRandomizeRequest,
    svc: GarageService = Depends(get_garage_service),
):
    return {"data": {"selection": svc.randomize(payload.selection)}}


@router.post("/buy-vehicle/{vehicle_id}")
async def buy_vehicle(
    vehicle_id: str,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(get_gamification_service),
):
    return {"data": await svc.buy_vehicle(user.id, vehicle_id)}


@router.post("/select-vehicle/{vehicle_id}")
async def select_vehicle(
    vehicle_id: str,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(get_gamification_service),
):
    return {"data": await svc.select_vehicle(user.id, vehicle_id)}


@router.post("/buy-item/{item_id}")
async def buy_item(
    item_id: str,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(get_gamification_service),
):
    return {"data": await svc.buy_item(user.id, item_id)}


@router.post("/equip-item")
async def equip_item(
    payload: EquipItemRequest,
    user: User = Depends(get_current_user),
    svc: GamificationService = Depends(get_gamification_service),
):
    return {"data": await svc.equip_item(user.id, vehicle_id=payload.vehicle_id, item_type=payload.item_type, item_id=payload.item_id)}
