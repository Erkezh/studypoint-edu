from __future__ import annotations

import random
import string
import uuid
import re

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password
from app.db.session import get_db_session
from app.models.classroom import Classroom, Enrollment
from app.models.enums import UserRole
from app.models.user import User
from app.models.profile import StudentProfile
from app.repositories.user_repo import UserRepository
from app.schemas.teacher import TeacherCreateStudentRequest, TeacherCreateStudentResponse
from app.utils.time import utc_now


def _transliterate_cyrillic(text: str) -> str:
    """Basic transliteration from Cyrillic to Latin for usernames."""
    mapping = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
        'я': 'ya', 'ә': 'a', 'і': 'i', 'ң': 'n', 'ғ': 'gh', 'ү': 'u', 'ұ': 'u', 'қ': 'q',
        'ө': 'o', 'һ': 'h'
    }
    
    # lowercase & remove special characters
    text = text.lower().strip()
    res = []
    for char in text:
        if char in mapping:
            res.append(mapping[char])
        elif re.match(r'[a-z0-9]', char):
            res.append(char)
            
    return ''.join(res)


def _generate_password(length: int = 6) -> str:
    # Use clearly distinguishable characters
    chars = "abcdefghjkmnpqrstuvwxyz23456789"
    return ''.join(random.choice(chars) for _ in range(length))


class TeacherService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def _generate_unique_username(self, base_username: str) -> str:
        """Find an available username by appending an integer if necessary."""
        # Check base first
        # We store username in the `email` field
        exists = await self.users.get_by_email(base_username)
        if not exists:
            return base_username
            
        counter = 1
        while True:
            candidate = f"{base_username}{counter}"
            exists = await self.users.get_by_email(candidate)
            if not exists:
                return candidate
            counter += 1
        return ""

    async def create_student(self, teacher_id: str, req: TeacherCreateStudentRequest) -> TeacherCreateStudentResponse:
        teacher_uuid = uuid.UUID(teacher_id)
        
        # Verify teacher exists
        teacher = await self.users.get_by_id(teacher_id)
        if not teacher or teacher.role != UserRole.TEACHER:
            raise AppError(status_code=403, code="forbidden", message="Only teachers can generate students")
            
        full_name = f"{req.first_name} {req.last_name}".strip()
        
        # Build base username
        first_trans = _transliterate_cyrillic(req.first_name)
        last_trans = _transliterate_cyrillic(req.last_name)
        
        if not first_trans and not last_trans:
            base_username = f"student{random.randint(1000, 9999)}"
        else:
            base_username = f"{first_trans}.{last_trans}"
            
        username = await self._generate_unique_username(base_username)
        password = _generate_password()
        password_hash = hash_password(password)
        
        student = User(
            email=username, # We hijack email column to store the generated username
            password_hash=password_hash,
            full_name=full_name,
            role=UserRole.STUDENT,
            is_active=True,
            teacher_id=teacher_uuid
        )
        self.session.add(student)
        await self.session.flush() # flush to get student.id
        
        # Create profile
        profile = StudentProfile(
            user_id=student.id,
            grade_level=req.grade_id
        )
        self.session.add(profile)
        
        # Enroll if classroom_id is provided
        if req.classroom_id:
            try:
                classroom_uuid = uuid.UUID(req.classroom_id)
                # Verify classroom belongs to teacher
                cls_stmt = select(Classroom).where(Classroom.id == classroom_uuid, Classroom.teacher_id == teacher_uuid)
                classroom = (await self.session.execute(cls_stmt)).scalar_one_or_none()
                if classroom:
                    enrollment = Enrollment(
                        classroom_id=classroom_uuid,
                        student_id=student.id,
                        enrolled_at=utc_now()
                    )
                    self.session.add(enrollment)
            except ValueError:
                pass # invalid classroom ID format
                
        await self.session.flush()
        
        return TeacherCreateStudentResponse(
            id=str(student.id),
            full_name=student.full_name,
            username=username,
            password=password
        )
