from __future__ import annotations

import json
import shutil
import tempfile
import uuid
from pathlib import Path

import jsonschema
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import AppError
from app.plugins.schemas import PluginCreate, PluginManifest
from app.plugins.security import PluginSecurityError, scan_zip_contents
from app.repositories.plugin_repo import PluginRepository


class PluginService:
    """Сервис для работы с плагинами: загрузка, валидация, сохранение."""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = PluginRepository(session)
        self.plugins_dir = Path(settings.plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

    async def upload_plugin(self, zip_file: UploadFile) -> dict:
        """Загружает и валидирует плагин из ZIP файла.
        
        Шаги:
        1. Сохраняет ZIP во временную директорию
        2. Проверяет размер и безопасность
        3. Распаковывает и находит manifest.json
        4. Валидирует manifest по JSON Schema
        5. Проверяет наличие entry файла
        6. Сохраняет в /static/plugins/{plugin_id}/{version}/
        7. Сохраняет метаданные в БД
        
        Returns:
            dict с информацией о загруженном плагине
        """
        # Сохраняем ZIP во временную директорию
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / zip_file.filename or "plugin.zip"
            
            # Читаем файл
            content = await zip_file.read()
            temp_path.write_bytes(content)
            
            # Security scan
            try:
                scan_zip_contents(temp_path, max_size_mb=settings.plugin_max_size_mb)
            except PluginSecurityError as e:
                raise AppError(status_code=400, code="plugin_security_error", message=str(e))
            
            # Распаковываем во временную директорию
            extract_dir = Path(temp_dir) / "extracted"
            extract_dir.mkdir()
            
            import zipfile
            try:
                with zipfile.ZipFile(temp_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
            except zipfile.BadZipFile:
                raise AppError(status_code=400, code="invalid_zip", message="Некорректный ZIP файл")
            
            # Ищем manifest.json
            manifest_path = extract_dir / "manifest.json"
            if not manifest_path.exists():
                raise AppError(
                    status_code=400,
                    code="manifest_not_found",
                    message="manifest.json не найден в корне архива"
                )
            
            # Читаем и валидируем manifest
            try:
                manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise AppError(
                    status_code=400,
                    code="invalid_manifest_json",
                    message=f"Некорректный JSON в manifest.json: {str(e)}"
                )
            
            # Валидация по JSON Schema
            schema_path = Path(__file__).parent / "manifest_schema.json"
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            
            try:
                jsonschema.validate(instance=manifest_data, schema=schema)
            except jsonschema.ValidationError as e:
                raise AppError(
                    status_code=400,
                    code="manifest_validation_error",
                    message=f"Ошибка валидации manifest.json: {e.message}"
                )
            
            # Парсим в Pydantic схему
            try:
                manifest = PluginManifest.model_validate(manifest_data)
            except Exception as e:
                raise AppError(
                    status_code=400,
                    code="manifest_parse_error",
                    message=f"Ошибка парсинга manifest: {str(e)}"
                )
            
            # Проверяем наличие entry файла
            entry_path = extract_dir / manifest.entry
            if not entry_path.exists():
                raise AppError(
                    status_code=400,
                    code="entry_not_found",
                    message=f"Entry файл не найден: {manifest.entry}"
                )
            
            # Используем manifest.id как уникальный идентификатор плагина
            # Это позволяет иметь несколько версий одного плагина с одинаковым ID
            plugin_id = manifest.id
            
            # Проверяем, не существует ли уже такой плагин с такой версией
            # Ищем по plugin_id и версии
            existing = await self.repo.get_by_plugin_id_and_version(plugin_id, manifest.version)
            if existing:
                # Если плагин не опубликован, удаляем старый и заменяем новым
                if not existing.is_published:
                    # Удаляем старый плагин из БД
                    await self.repo.delete(existing.id)
                    # Удаляем старые файлы
                    old_plugin_dir = self.plugins_dir / plugin_id / manifest.version
                    if old_plugin_dir.exists():
                        shutil.rmtree(old_plugin_dir)
                else:
                    # Если плагин опубликован, не разрешаем замену
                    raise AppError(
                        status_code=409,
                        code="plugin_exists",
                        message=f"Плагин {plugin_id} версии {manifest.version} уже опубликован и не может быть заменен"
                    )
            
            # Сохраняем плагин в постоянную директорию
            # Путь: static/plugins/{plugin_id}/{version}/
            plugin_dir = self.plugins_dir / plugin_id / manifest.version
            if plugin_dir.exists():
                # Если директория существует (но записи в БД нет), удаляем
                shutil.rmtree(plugin_dir)
            plugin_dir.mkdir(parents=True, exist_ok=True)
            
            # Копируем все файлы
            # Используем более надежный способ копирования
            for item in extract_dir.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(extract_dir)
                    target_path = plugin_dir / rel_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_path)
            
            # Генерируем UUID для БД (для уникальности записи)
            # Но используем plugin_id (manifest.id) для пути к файлам
            plugin_uuid = str(uuid.uuid4())
            
            # Сохраняем в БД
            plugin = await self.repo.create({
                "id": plugin_uuid,  # UUID для БД
                "plugin_id": plugin_id,  # ID из manifest для пути к файлам
                "name": manifest.name,
                "version": manifest.version,
                "entry": manifest.entry,
                "api_version": manifest.api_version,
                "capabilities": manifest.capabilities,
                "height": manifest.height,
                "is_published": False,  # По умолчанию не опубликован
                "manifest_data": manifest_data,
            })
            
            return {
                "id": plugin.id,
                "plugin_id": plugin.plugin_id,  # ID для пути к файлам
                "name": plugin.name,
                "version": plugin.version,
                "entry": plugin.entry,
                "api_version": plugin.api_version,
                "capabilities": plugin.capabilities,
                "height": plugin.height,
                "is_published": plugin.is_published,
            }

    async def list_plugins(self) -> list[dict]:
        """Получить список всех загруженных плагинов."""
        plugins = await self.repo.list_all()
        return [
            {
                "id": p.id,
                "plugin_id": p.plugin_id,  # ID для пути к файлам
                "name": p.name,
                "version": p.version,
                "entry": p.entry,
                "api_version": p.api_version,
                "capabilities": p.capabilities,
                "height": p.height,
                "is_published": p.is_published,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in plugins
        ]

    async def publish_plugin(self, plugin_id: str, is_published: bool) -> dict:
        """Опубликовать или скрыть плагин."""
        plugin = await self.repo.update_published(plugin_id, is_published)
        if not plugin:
            raise AppError(status_code=404, code="plugin_not_found", message="Плагин не найден")
        
        return {
            "id": plugin.id,
            "is_published": plugin.is_published,
        }

    async def delete_plugin(self, plugin_id: str) -> dict:
        """Удаляет плагин (только если не опубликован).
        
        Args:
            plugin_id: UUID плагина в БД (не plugin_id из manifest)
        
        Returns:
            dict с результатом удаления
        """
        plugin = await self.repo.get_by_id(plugin_id)
        if not plugin:
            raise AppError(status_code=404, code="plugin_not_found", message="Плагин не найден")
        
        # Проверяем, что плагин не опубликован
        if plugin.is_published:
            raise AppError(
                status_code=403,
                code="cannot_delete_published",
                message="Нельзя удалить опубликованный плагин. Сначала скройте его."
            )
        
        # Удаляем файлы плагина
        plugin_dir = self.plugins_dir / plugin.plugin_id / plugin.version
        if plugin_dir.exists():
            shutil.rmtree(plugin_dir)
        
        # Удаляем из БД
        await self.repo.delete(plugin_id)
        
        return {
            "id": plugin_id,
            "deleted": True,
        }

    async def evaluate_answer(
        self,
        plugin_id: str,
        task_id: str,
        user_answer: dict,
    ) -> dict:
        """Проверяет ответ пользователя для плагина.
        
        plugin_id - это plugin_id из manifest (не UUID из БД).
        Для примера math-addition-example проверяем сложение чисел.
        """
        # Ищем плагин по plugin_id (из manifest)
        plugin = await self.repo.get_by_plugin_id(plugin_id)
        if not plugin:
            raise AppError(status_code=404, code="plugin_not_found", message="Плагин не найден")
        
        # Простая логика проверки для примера math-addition-example
        if plugin_id == "math-addition-example":
            # Извлекаем ответ пользователя
            user_answer_value = user_answer.get("answer")
            question_text = user_answer.get("question", "")
            
            # Парсим вопрос для получения правильного ответа
            # Формат: "5 + 3 = ?"
            import re
            match = re.match(r'(\d+)\s*\+\s*(\d+)\s*=\s*\?', question_text)
            if match:
                a = int(match.group(1))
                b = int(match.group(2))
                correct_answer = a + b
                
                is_correct = user_answer_value == correct_answer
                score = 1.0 if is_correct else 0.0
                
                if is_correct:
                    explanation = f"Правильно! {a} + {b} = {correct_answer}"
                else:
                    explanation = f"Неправильно. Правильный ответ: {a} + {b} = {correct_answer}. Вы ввели: {user_answer_value}"
                
                return {
                    "correct": is_correct,
                    "score": score,
                    "explanation": explanation,
                }
            else:
                # Если не удалось распарсить вопрос, возвращаем ошибку
                return {
                    "correct": False,
                    "score": 0.0,
                    "explanation": "Не удалось распознать вопрос",
                }
        
        # Логика проверки для drag-drop-math-example
        if plugin_id == "drag-drop-math-example":
            # Извлекаем ответ пользователя
            user_a = user_answer.get("a")
            user_b = user_answer.get("b")
            user_sum = user_answer.get("answer")
            question_text = user_answer.get("question", "")
            
            # Отладочная информация (в продакшене убрать)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Drag-drop check: a={user_a}, b={user_b}, sum={user_sum}, question={question_text}")
            
            # Парсим вопрос для получения правильного ответа
            # Формат: "X + Y = Z" где Z - правильный ответ (сумма)
            import re
            match = re.search(r'=\s*(\d+)$', question_text)
            if match:
                correct_sum = int(match.group(1))  # Правильный ответ из вопроса
                
                # Проверяем: сумма перетащенных чисел должна равняться правильному ответу
                # Числа могут быть в любом порядке, поэтому проверяем только сумму
                if user_a is not None and user_b is not None:
                    calculated_sum = user_a + user_b
                    is_correct = (calculated_sum == correct_sum)
                    score = 1.0 if is_correct else 0.0
                    
                    if is_correct:
                        explanation = f"Правильно! {user_a} + {user_b} = {correct_sum}"
                    else:
                        # Находим правильные числа для объяснения
                        # Правильные числа - это те, которые в сумме дают correct_sum
                        # Показываем пример правильного ответа
                        explanation = f"Неправильно. Сумма должна быть {correct_sum}. Вы указали: {user_a} + {user_b} = {calculated_sum}"
                    
                    return {
                        "correct": is_correct,
                        "score": score,
                        "explanation": explanation,
                    }
                else:
                    return {
                        "correct": False,
                        "score": 0.0,
                        "explanation": f"Не получены значения a и b. Получено: a={user_a}, b={user_b}",
                    }
            else:
                # Если не удалось распарсить правильный ответ из вопроса
                # Пытаемся извлечь из формата "X + Y = Z"
                match_full = re.match(r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)', question_text)
                if match_full:
                    correct_sum = int(match_full.group(3))
                    if user_a is not None and user_b is not None:
                        calculated_sum = user_a + user_b
                        is_correct = (calculated_sum == correct_sum)
                        score = 1.0 if is_correct else 0.0
                        
                        if is_correct:
                            explanation = f"Правильно! {user_a} + {user_b} = {correct_sum}"
                        else:
                            explanation = f"Неправильно. Сумма должна быть {correct_sum}. Вы указали: {user_a} + {user_b} = {calculated_sum}"
                        
                        return {
                            "correct": is_correct,
                            "score": score,
                            "explanation": explanation,
                        }
                
                # Если не удалось распарсить вопрос
                return {
                    "correct": False,
                    "score": 0.0,
                    "explanation": f"Не удалось распознать правильный ответ из вопроса: '{question_text}'. Получено: a={user_a}, b={user_b}, sum={user_sum}",
                }
        
        # Для других плагинов - базовая проверка
        # В будущем можно добавить специфичную логику для каждого плагина
        return {
            "correct": False,
            "score": 0.0,
            "explanation": "Логика проверки для этого плагина еще не реализована",
        }
