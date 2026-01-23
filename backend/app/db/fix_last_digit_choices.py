"""
Скрипт для исправления вариантов ответов в вопросах типа "last digit"
Добавляет правильный ответ, если его нет среди вариантов
"""
from __future__ import annotations

import asyncio
import re
from sqlalchemy import select

from app.core.config import settings
from app.db.session import init_engine, get_sessionmaker
from app.models.question import Question
from app.models.enums import QuestionType


async def fix_last_digit_choices():
    """Исправляет варианты ответов для всех вопросов типа 'last digit'"""
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
                
                # Получаем текущие варианты
                choices = question.data.get("choices") or question.data.get("options") or []
                
                # Проверяем, есть ли правильный ответ среди вариантов
                has_correct = False
                for choice in choices:
                    if isinstance(choice, dict):
                        choice_text = str(choice.get("text") or choice.get("value") or choice.get("label") or "").strip()
                    else:
                        choice_text = str(choice).strip()
                    
                    if choice_text == last_digit:
                        has_correct = True
                        break
                
                # Если правильного ответа нет, добавляем его
                if not has_correct and choices:
                    # Определяем формат вариантов (объекты или простые значения)
                    if isinstance(choices[0], dict):
                        # Если варианты - объекты, добавляем новый объект
                        # Находим максимальный ID или используем следующую букву
                        max_id = "A"
                        for choice in choices:
                            if isinstance(choice, dict):
                                choice_id = str(choice.get("id") or "")
                                if choice_id and len(choice_id) == 1 and choice_id.isalpha():
                                    if choice_id > max_id:
                                        max_id = choice_id
                        
                        # Следующая буква после максимальной
                        next_id = chr(ord(max_id) + 1) if max_id != "Z" else "A"
                        
                        # Добавляем правильный ответ
                        new_choice = {"id": next_id, "text": last_digit}
                        choices.append(new_choice)
                        
                        # Обновляем correct_answer
                        question.correct_answer = {"choice": next_id}
                    else:
                        # Если варианты - простые значения, просто добавляем правильный ответ
                        choices.append(last_digit)
                        # Обновляем correct_answer на индекс нового варианта
                        question.correct_answer = {"choice": str(len(choices) - 1)}
                    
                    # Обновляем data
                    if "choices" in question.data:
                        question.data["choices"] = choices
                    elif "options" in question.data:
                        question.data["options"] = choices
                    
                    fixed_count += 1
                    print(f"Fixed question {question.id}: '{question.prompt}' - added correct answer '{last_digit}' to choices")
            
            await session.commit()
            print(f"\nFixed {fixed_count} questions")
        except Exception as e:
            await session.rollback()
            print(f"Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(fix_last_digit_choices())
