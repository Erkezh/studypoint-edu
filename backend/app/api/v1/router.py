from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.routes import admin, analytics, assignments, auth, awards, catalog, classrooms, family, health, me, practice, reports, teacher, users, quiz, student_quiz, notifications

api_router_v1 = APIRouter()

api_router_v1.include_router(health.router, tags=["Health"])
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
api_router_v1.include_router(quiz.router, prefix="/teacher/quizzes", tags=["Quiz"])
api_router_v1.include_router(student_quiz.router, prefix="/student/quizzes", tags=["StudentQuiz"])
api_router_v1.include_router(family.router, prefix="/family", tags=["Family"])
api_router_v1.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router_v1.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
