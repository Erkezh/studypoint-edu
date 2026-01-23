from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import admin, analytics, assignments, auth, awards, catalog, classrooms, me, practice, reports, teacher, users

api_router_v1 = APIRouter()

api_router_v1.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router_v1.include_router(users.router, prefix="/users", tags=["Users"])
api_router_v1.include_router(me.router, prefix="/me", tags=["Me"])
api_router_v1.include_router(catalog.router, tags=["Catalog"])
api_router_v1.include_router(practice.router, prefix="/practice", tags=["Practice"])
api_router_v1.include_router(classrooms.router, prefix="/classrooms", tags=["Classrooms"])
api_router_v1.include_router(assignments.router, prefix="/assignments", tags=["Assignments"])
api_router_v1.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router_v1.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router_v1.include_router(awards.router, prefix="/awards", tags=["Awards"])
api_router_v1.include_router(teacher.router, prefix="/teacher", tags=["Teacher"])
api_router_v1.include_router(admin.router, prefix="/admin", tags=["Admin"])
