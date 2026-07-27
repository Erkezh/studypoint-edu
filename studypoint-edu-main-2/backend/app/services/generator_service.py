"""Сервис для безопасного выполнения генераторов кода задач"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class GeneratorService:
    """Сервис для выполнения генераторов задач"""
    
    @staticmethod
    def validate_generator_interface(code: str) -> tuple[bool, str | None]:
        """
        Проверяет, что код генератора соответствует требуемому интерфейсу.
        
        Генератор должен экспортировать функцию generate() которая:
        - Принимает опциональные параметры (metadata)
        - Возвращает объект с полями:
          - prompt: str - текст задачи
          - type: str - тип задачи (MCQ, NUMERIC, TEXT, etc.)
          - data: dict - данные задачи (варианты ответов, и т.д.)
          - correct_answer: dict - правильный ответ
          - explanation: str - объяснение (опционально)
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Базовая проверка синтаксиса
            compile(code, '<string>', 'exec')
            
            # Проверяем наличие функции generate
            if 'def generate' not in code and 'function generate' not in code and 'const generate' not in code:
                return False, "Generator code must export a 'generate' function"
            
            # Проверяем наличие экспорта
            if 'export' not in code and 'module.exports' not in code:
                return False, "Generator code must export the generate function"
            
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error in generator code: {str(e)}"
        except Exception as e:
            return False, f"Error validating generator code: {str(e)}"
    
    @staticmethod
    def execute_generator(
        code: str,
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Выполняет генератор кода и возвращает задачу.
        
        Args:
            code: Код генератора
            metadata: Метаданные для генератора (параметры, настройки)
            
        Returns:
            Словарь с задачей:
            {
                "prompt": str,
                "type": str,
                "data": dict,
                "correct_answer": dict,
                "explanation": str (опционально)
            }
        """
        # ВАЖНО: В продакшене это должно выполняться в изолированной среде
        # (Docker container, sandbox, или отдельный сервис)
        # Для разработки выполняем напрямую, но с ограничениями
        
        try:
            # Преобразуем JavaScript-подобный код в Python
            # Заменяем JavaScript комментарии на Python комментарии
            python_code = code
            # Заменяем // комментарии на # (только если не в строке)
            import re
            # Простая замена // комментариев на # (может быть неточной, но для базовых случаев работает)
            lines = python_code.split('\n')
            python_lines = []
            for line in lines:
                # Проверяем, не является ли // частью строки
                if '//' in line:
                    # Разделяем на части до и после //
                    parts = line.split('//', 1)
                    if len(parts) == 2:
                        # Проверяем, не является ли // частью строки (простая проверка)
                        before_comment = parts[0]
                        if '"' not in before_comment and "'" not in before_comment:
                            # Это комментарий, заменяем на #
                            python_lines.append(parts[0].rstrip() + '  # ' + parts[1].strip())
                        else:
                            python_lines.append(line)
                    else:
                        python_lines.append(line)
                else:
                    python_lines.append(line)
            python_code = '\n'.join(python_lines)
            
            # Удаляем импорты random и math из кода, так как они уже доступны в контексте
            # Это позволяет генератору использовать import random внутри функции
            python_code = re.sub(r'^import\s+random\s*$', '# import random (already available)', python_code, flags=re.MULTILINE)
            python_code = re.sub(r'^from\s+random\s+import.*$', '# from random import (already available)', python_code, flags=re.MULTILINE)
            python_code = re.sub(r'^import\s+math\s*$', '# import math (already available)', python_code, flags=re.MULTILINE)
            python_code = re.sub(r'^from\s+math\s+import.*$', '# from math import (already available)', python_code, flags=re.MULTILINE)
            
            # Импортируем модули заранее
            import random as random_module
            import math as math_module
            
            # Создаем безопасную функцию __import__ для разрешенных модулей
            def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
                """Безопасный импорт, разрешающий только random и math"""
                allowed_modules = {'random', 'math'}
                if name in allowed_modules:
                    if name == 'random':
                        return random_module
                    elif name == 'math':
                        return math_module
                raise ImportError(f"Import of '{name}' is not allowed. Only 'random' and 'math' are allowed.")
            
            # Создаем безопасный контекст выполнения
            safe_globals = {
                '__builtins__': {
                    'range': range,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'min': min,
                    'max': max,
                    'abs': abs,
                    'round': round,
                    'sum': sum,
                    'print': print,  # Для отладки
                    '__import__': safe_import,  # Безопасный импорт
                },
                # Делаем модули доступными напрямую
                'random': random_module,
                'math': math_module,
                'metadata': metadata or {},
            }
            
            safe_locals = {}
            
            # Выполняем код генератора
            exec(python_code, safe_globals, safe_locals)
            
            # Ищем функцию generate
            generate_func = None
            if 'generate' in safe_locals:
                generate_func = safe_locals['generate']
            elif 'generate' in safe_globals:
                generate_func = safe_globals['generate']
            elif hasattr(safe_locals.get('module', {}), 'exports'):
                generate_func = safe_locals['module'].exports.get('generate')
            
            if generate_func is None:
                raise ValueError("Generator function 'generate' not found")
            
            # Вызываем генератор
            if callable(generate_func):
                result = generate_func(metadata or {})
            else:
                raise ValueError("'generate' is not callable")
            
            # Валидируем результат
            if not isinstance(result, dict):
                raise ValueError("Generator must return a dictionary")
            
            required_fields = ['prompt', 'type', 'data', 'correct_answer']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Generator result must contain '{field}' field")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing generator: {e}", exc_info=True)
            raise ValueError(f"Generator execution failed: {str(e)}")
    
    @staticmethod
    async def validate_answer(
        generator_code: str,
        question_data: dict[str, Any],
        submitted_answer: dict[str, Any],
        metadata: dict[str, Any] | None = None
    ) -> tuple[bool, str | None]:
        """
        Проверяет ответ студента используя логику генератора.
        
        Args:
            generator_code: Код генератора
            question_data: Данные задачи (которые были сгенерированы)
            submitted_answer: Ответ студента
            metadata: Метаданные генератора
            
        Returns:
            (is_correct, explanation)
        """
        try:
            # Правильный ответ уже должен быть в question_data
            correct_answer_data = question_data.get('correct_answer', {})
            
            # Сравниваем ответы
            question_type = question_data.get('type', 'MCQ')
            
            # Для MCQ сравниваем значения
            if question_type == 'MCQ':
                # submitted_answer может быть строкой или объектом
                # С фронтенда приходит: {choice: "..."} или {answer: "..."}
                if isinstance(submitted_answer, str):
                    submitted = submitted_answer
                else:
                    # Проверяем разные возможные поля
                    submitted = (
                        submitted_answer.get('choice') or 
                        submitted_answer.get('answer') or 
                        submitted_answer.get('value') or 
                        submitted_answer.get('id') or
                        (submitted_answer if not isinstance(submitted_answer, dict) else None)
                    )
                
                # correct_answer из генератора имеет формат {"answer": "..."}
                correct = (
                    correct_answer_data.get('answer') or 
                    correct_answer_data.get('value') or 
                    correct_answer_data.get('choice') or
                    correct_answer_data.get('id')
                )
                
                # Сравниваем как строки (без учета регистра и пробелов)
                is_correct = str(submitted).strip().lower() == str(correct).strip().lower()
                
                logger.info(
                    f"MCQ answer validation: submitted={submitted}, correct={correct}, is_correct={is_correct}"
                )
            # Для NUMERIC сравниваем числовые значения
            elif question_type == 'NUMERIC':
                try:
                    if isinstance(submitted_answer, (int, float)):
                        submitted = float(submitted_answer)
                    else:
                        submitted = float(submitted_answer.get('answer', 0))
                    correct = float(correct_answer_data.get('answer', 0))
                    is_correct = abs(submitted - correct) < 0.001  # Допуск для float
                except (ValueError, TypeError):
                    is_correct = False
            # Для TEXT сравниваем строки (case-insensitive)
            elif question_type == 'TEXT':
                if isinstance(submitted_answer, str):
                    submitted = submitted_answer.strip().lower()
                else:
                    submitted = str(submitted_answer.get('answer', '')).strip().lower()
                correct = str(correct_answer_data.get('answer', '')).strip().lower()
                is_correct = submitted == correct
            else:
                # Для других типов сравниваем напрямую
                is_correct = str(submitted_answer).strip() == str(correct_answer_data).strip()
            
            explanation = question_data.get('explanation', '')
            return is_correct, explanation
            
        except Exception as e:
            logger.error(f"Error validating answer: {e}", exc_info=True)
            return False, f"Validation error: {str(e)}"
