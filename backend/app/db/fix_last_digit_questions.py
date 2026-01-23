"""
Скрипт для исправления правильных ответов в вопросах типа "last digit"
"""
from __future__ import annotations

import asyncio
import re
from sqlalchemy import select

from app.core.config import settings
from app.db.session import init_engine, get_sessionmaker
from app.models.question import Question
from app.models.enums import QuestionType


async def fix_last_digit_questions():
    """Исправляет правильные ответы для всех вопросов типа 'last digit'"""
    # Инициализируем engine
    init_engine(settings.database_url)
    sessionmaker = get_sessionmaker()
    
    async with sessionmaker() as session:
        try:
            # Находим все MCQ вопросы с "last digit" в prompt
            stmt = select(Question).where(
                Question.type == QuestionType.MCQ
            ).where(
                Question.prompt.ilike("%last digit%")
            )
            result = await session.execute(stmt)
            questions = result.scalars().all()
            
            fixed_count = 0
            for question in questions:
                # Извлекаем число из вопроса
                numbers = re.findall(r'\d+', question.prompt)
                if not numbers:
                    continue
                
                number = int(numbers[0])
                last_digit = str(number % 10)
                
                # Находим правильный вариант в choices
                choices = question.data.get("choices") or question.data.get("options") or []
                correct_choice_id = None
                
                for idx, choice in enumerate(choices):
                    if isinstance(choice, dict):
                        # Проверяем text, value, label
                        choice_text = str(choice.get("text") or choice.get("value") or choice.get("label") or "").strip()
                        choice_id = str(choice.get("id") or "").strip()
                    else:
                        choice_text = str(choice).strip()
                        choice_id = str(idx)
                    
                    if choice_text == last_digit:
                        correct_choice_id = choice_id if choice_id else str(idx)
                        break
                
                # Если нашли правильный вариант и он отличается от текущего
                if correct_choice_id:
                    current_correct = question.correct_answer.get("choice") if question.correct_answer else None
                    if current_correct != correct_choice_id:
                        question.correct_answer = {"choice": correct_choice_id}
                        fixed_count += 1
                        print(f"Fixed question {question.id}: '{question.prompt}' - correct answer: {correct_choice_id} (was: {current_correct})")
            
            await session.commit()
            print(f"\nFixed {fixed_count} questions")
        except Exception as e:
            await session.rollback()
            print(f"Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(fix_last_digit_questions())
