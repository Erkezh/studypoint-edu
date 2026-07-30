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


def _generate_password(length: int = 10) -> str:
    """Generate a strong password with uppercase, lowercase, digits and symbols."""
    import string
    lowercase = "abcdefghjkmnpqrstuvwxyz"
    uppercase = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    digits = "23456789"
    symbols = "!@#$%"
    # Ensure at least one of each category
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(symbols),
    ]
    all_chars = lowercase + uppercase + digits + symbols
    password += [random.choice(all_chars) for _ in range(length - 4)]
    random.shuffle(password)
    return ''.join(password)


class TeacherService:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def _generate_smart_username(self, first_name: str, last_name: str) -> str:
        """Generate a smart username based on name, surname, combination, or numbers."""
        fn = _transliterate_cyrillic(first_name)
        ln = _transliterate_cyrillic(last_name)

        candidates = []

        # 1. Base clean candidates (first name, last name, or combinations)
        if fn:
            candidates.append(fn)
        if ln:
            candidates.append(ln)
        if fn and ln:
            candidates.append(f"{fn}{ln}")
            candidates.append(f"{fn}.{ln}")
            candidates.append(f"{fn}_{ln}")

        # Check clean candidates first
        for candidate in candidates:
            if candidate and not await self.users.get_by_email(candidate):
                return candidate

        # 2. Add numbers if base variants are taken (fn1, ln1, fnln1, fn2, ln2, fnln2...)
        counter = 1
        while counter < 1000:
            numbered_candidates = []
            if fn:
                numbered_candidates.append(f"{fn}{counter}")
            if ln:
                numbered_candidates.append(f"{ln}{counter}")
            if fn and ln:
                numbered_candidates.append(f"{fn}{ln}{counter}")

            for candidate in numbered_candidates:
                if candidate and not await self.users.get_by_email(candidate):
                    return candidate
            counter += 1

        # 3. Fallback: user + numbers
        counter = 1
        while True:
            candidate = f"user{counter}"
            if not await self.users.get_by_email(candidate):
                return candidate
            counter += 1

    async def create_student(self, teacher_id: str, req: TeacherCreateStudentRequest) -> TeacherCreateStudentResponse:
        teacher_uuid = teacher_id if isinstance(teacher_id, uuid.UUID) else uuid.UUID(str(teacher_id))
        
        # Verify teacher exists
        teacher = await self.users.get_by_id(teacher_id)
        if not teacher or teacher.role != UserRole.TEACHER:
            raise AppError(status_code=403, code="forbidden", message="Only teachers can generate students")
            
        full_name = f"{req.first_name} {req.last_name}".strip()

        # Generate smart username based on first name & last name
        username = await self._generate_smart_username(req.first_name, req.last_name)
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
            grade_level=req.grade_id,
            plain_password=password
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
