"""Redis-based presence service for tracking which students are currently practicing."""
from __future__ import annotations

import json
import logging
from datetime import datetime

from app.utils.redis import get_redis
from app.utils.time import utc_now

logger = logging.getLogger(__name__)

PRESENCE_KEY_PREFIX = "student:presence:"
PRESENCE_TTL_SEC = 60  # Auto-expire after 60s of no heartbeat


async def update_presence(
    *,
    user_id: str,
    skill_id: int,
    skill_name: str,
    smartscore: int,
    correct: int,
    wrong: int,
    questions_answered: int,
    session_id: str,
) -> None:
    """Write/refresh a student's presence in Redis with a 60s TTL."""
    try:
        redis = get_redis()
        key = f"{PRESENCE_KEY_PREFIX}{user_id}"
        data = {
            "skill_id": skill_id,
            "skill_name": skill_name,
            "smartscore": smartscore,
            "correct": correct,
            "wrong": wrong,
            "questions_answered": questions_answered,
            "session_id": session_id,
            "updated_at": utc_now().isoformat(),
        }
        await redis.set(key, json.dumps(data), ex=PRESENCE_TTL_SEC)
    except Exception as exc:
        logger.warning("Failed to update presence for user %s: %s", user_id, exc)


async def remove_presence(user_id: str) -> None:
    """Remove a student's presence when they finish a session."""
    try:
        redis = get_redis()
        key = f"{PRESENCE_KEY_PREFIX}{user_id}"
        await redis.delete(key)
    except Exception as exc:
        logger.warning("Failed to remove presence for user %s: %s", user_id, exc)


async def get_presence(user_id: str) -> dict | None:
    """Get a single student's presence data, or None if not active."""
    try:
        redis = get_redis()
        key = f"{PRESENCE_KEY_PREFIX}{user_id}"
        raw = await redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("Failed to get presence for user %s: %s", user_id, exc)
        return None


async def get_active_students(student_ids: list[str]) -> list[dict]:
    """Check which students from the list are currently active.
    
    Returns a list of dicts with student_id + presence data for active ones.
    """
    if not student_ids:
        return []

    active = []
    try:
        redis = get_redis()
        # Use pipeline for efficiency
        pipe = redis.pipeline()
        for sid in student_ids:
            pipe.get(f"{PRESENCE_KEY_PREFIX}{sid}")
        results = await pipe.execute()

        now = utc_now()
        for sid, raw in zip(student_ids, results):
            if raw is None:
                continue
            try:
                data = json.loads(raw)
                # Calculate seconds since last activity
                updated_at = datetime.fromisoformat(data["updated_at"])
                delta = (now - updated_at).total_seconds()
                data["student_id"] = sid
                data["last_active_seconds_ago"] = int(delta)
                active.append(data)
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning("Malformed presence data for %s: %s", sid, exc)
                continue
    except Exception as exc:
        logger.warning("Failed to get active students: %s", exc)

    return active
