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
from app.plugins.tsx_transformer import transform_tsx_to_html
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

    async def upload_tsx_plugin(
        self,
        file: UploadFile,
        plugin_name: str | None = None,
        grade_id: int | None = None,
        admin_service = None,
    ) -> dict:
        """Загружает TSX файл и создает плагин из него.
        
        Args:
            file: TSX файл
            plugin_name: Название плагина (если не указано, берется из имени файла)
            grade_id: ID класса для автоматического добавления в тест
            admin_service: Сервис администрирования для создания навыка
            
        Returns:
            dict с информацией о созданном плагине
        """
        import logging
        import re
        import zipfile
        from app.models.enums import QuestionType
        
        logger = logging.getLogger(__name__)
        logger.info(f"Starting TSX plugin upload: filename={file.filename}, plugin_name={plugin_name}, grade_id={grade_id}")
        
        # Читаем TSX код
        # Важно: FastAPI UploadFile можно прочитать только один раз
        try:
            # Сбрасываем позицию файла на начало (если он был прочитан ранее)
            if hasattr(file, 'seek') and hasattr(file.file, 'seek'):
                await file.seek(0)
            content = await file.read()
            tsx_code = content.decode("utf-8")
            logger.info(f"TSX file read successfully: {len(tsx_code)} characters")
            
            if not tsx_code or len(tsx_code.strip()) == 0:
                raise AppError(
                    status_code=400,
                    code="empty_file",
                    message="Файл пустой или не содержит TSX код"
                )
        except UnicodeDecodeError as e:
            raise AppError(
                status_code=400,
                code="file_encoding_error",
                message=f"Ошибка декодирования файла. Убедитесь, что файл в кодировке UTF-8: {str(e)}"
            )
        except Exception as e:
            if isinstance(e, AppError):
                raise
            raise AppError(
                status_code=400,
                code="file_read_error",
                message=f"Ошибка при чтении файла: {str(e)}"
            )
        
        # Определяем имя плагина
        if not plugin_name:
            plugin_name = Path(file.filename or "tsx-plugin").stem
            # Убираем расширение и делаем читаемым
            plugin_name = re.sub(r"[^a-zA-Z0-9\s-]", "", plugin_name)
            plugin_name = re.sub(r"\s+", "-", plugin_name).lower()
            if not plugin_name:
                plugin_name = "tsx-plugin"
        
        # Генерируем plugin_id из имени
        plugin_id = re.sub(r"[^a-zA-Z0-9-]", "", plugin_name.lower())[:32]
        if not plugin_id:
            plugin_id = f"tsx-{uuid.uuid4().hex[:8]}"
        
        version = "1.0.0"
        
        # Преобразуем TSX в HTML
        try:
            logger.info("Transforming TSX to HTML...")
            html_content = transform_tsx_to_html(tsx_code, plugin_name)
            logger.info(f"TSX transformed successfully: {len(html_content)} characters")
        except Exception as e:
            logger.error(f"TSX transformation error: {str(e)}", exc_info=True)
            raise AppError(
                status_code=400,
                code="tsx_transform_error",
                message=f"Ошибка при преобразовании TSX: {str(e)}"
            )
        
        # Создаем manifest
        manifest = PluginManifest(
            id=plugin_id,
            name=plugin_name,
            version=version,
            entry="index.html",
            apiVersion="1",
            capabilities={
                "submit": True,
                "explanation": True,
            },
            height=400,
        )
        
        # Сохраняем плагин
        plugin_dir = self.plugins_dir / plugin_id / version
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем файлы
        (plugin_dir / "index.html").write_text(html_content, encoding="utf-8")
        (plugin_dir / "manifest.json").write_text(
            manifest.model_dump_json(indent=2), encoding="utf-8"
        )
        
        # Создаем ZIP архив
        zip_path = plugin_dir.parent / f"{plugin_id}-{version}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(plugin_dir / "index.html", "index.html")
            zip_file.write(plugin_dir / "manifest.json", "manifest.json")
        
        # Сохраняем в БД
        # Генерируем UUID для БД (для уникальности записи)
        plugin_uuid = str(uuid.uuid4())
        
        # Используем словарь, как в upload_plugin
        logger.info(f"Creating plugin in database: plugin_id={plugin_id}, name={plugin_name}")
        plugin = await self.repo.create({
            "id": plugin_uuid,  # UUID для БД
            "plugin_id": plugin_id,  # ID из manifest для пути к файлам
            "name": plugin_name,
            "version": version,
            "entry": "index.html",
            "api_version": "1",
            "capabilities": manifest.capabilities,
            "height": manifest.height,
            "is_published": False,
            "manifest_data": manifest.model_dump(),
        })
        logger.info(f"Plugin created in database: id={plugin.id}, plugin_id={plugin.plugin_id}")
        
        result = {
            "id": str(plugin.id),
            "plugin_id": plugin_id,
            "name": plugin_name,
            "version": version,
            "is_published": False,
        }
        
        # Если указан grade_id, автоматически добавляем в тест
        if grade_id and admin_service:
            try:
                from app.schemas.admin import AddPluginToTestRequest
                add_req = AddPluginToTestRequest(
                    grade_id=grade_id,
                    plugin_id=plugin_id,
                    plugin_version=version,
                )
                test_result = await admin_service.add_plugin_to_test(add_req)
                result["added_to_test"] = test_result
            except Exception as e:
                # Не критично, если не удалось добавить в тест
                result["add_to_test_error"] = str(e)
        
        return result

    def _increment_version(self, version: str) -> str:
        """Увеличивает patch-версию (1.0.0 -> 1.0.1)."""
        parts = version.split(".")
        if len(parts) == 3:
            try:
                major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                return f"{major}.{minor}.{patch + 1}"
            except ValueError:
                pass
        # Если не удалось распарсить, просто добавляем .1
        return f"{version}.1"

    async def update_tsx_plugin(
        self,
        plugin_id: str,
        file: UploadFile,
    ) -> dict:
        """Обновляет существующий плагин новым TSX файлом.
        
        При обновлении автоматически увеличивается версия (1.0.0 -> 1.0.1).
        
        Args:
            plugin_id: UUID плагина в БД
            file: Новый TSX файл
            
        Returns:
            dict с информацией об обновленном плагине
        """
        import logging
        import re
        
        logger = logging.getLogger(__name__)
        logger.info(f"Updating TSX plugin: plugin_id={plugin_id}")
        
        # Находим плагин в БД
        plugin = await self.repo.get_by_id(plugin_id)
        if not plugin:
            raise AppError(status_code=404, code="plugin_not_found", message="Плагин не найден")
        
        old_version = plugin.version
        new_version = self._increment_version(old_version)
        logger.info(f"Incrementing version: {old_version} -> {new_version}")
        
        # Читаем TSX код
        try:
            if hasattr(file, 'seek') and hasattr(file.file, 'seek'):
                await file.seek(0)
            content = await file.read()
            tsx_code = content.decode("utf-8")
            logger.info(f"TSX file read successfully: {len(tsx_code)} characters")
            
            if not tsx_code or len(tsx_code.strip()) == 0:
                raise AppError(
                    status_code=400,
                    code="empty_file",
                    message="Файл пустой или не содержит TSX код"
                )
        except UnicodeDecodeError as e:
            raise AppError(
                status_code=400,
                code="file_encoding_error",
                message=f"Ошибка декодирования файла. Убедитесь, что файл в кодировке UTF-8: {str(e)}"
            )
        except Exception as e:
            if isinstance(e, AppError):
                raise
            raise AppError(
                status_code=400,
                code="file_read_error",
                message=f"Ошибка при чтении файла: {str(e)}"
            )
        
        # Преобразуем TSX в HTML
        try:
            logger.info("Transforming TSX to HTML...")
            html_content = transform_tsx_to_html(tsx_code, plugin.name)
            logger.info(f"TSX transformed successfully: {len(html_content)} characters")
        except Exception as e:
            logger.error(f"TSX transformation error: {str(e)}", exc_info=True)
            raise AppError(
                status_code=400,
                code="tsx_transform_error",
                message=f"Ошибка при преобразовании TSX: {str(e)}"
            )
        
        # Создаём новую директорию для новой версии
        new_plugin_dir = self.plugins_dir / plugin.plugin_id / new_version
        new_plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Копируем manifest.json из старой версии и обновляем версию
        old_plugin_dir = self.plugins_dir / plugin.plugin_id / old_version
        old_manifest_path = old_plugin_dir / "manifest.json"
        new_manifest_path = new_plugin_dir / "manifest.json"
        
        if old_manifest_path.exists():
            manifest_data = json.loads(old_manifest_path.read_text(encoding="utf-8"))
            manifest_data["version"] = new_version
            new_manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # Записываем новый index.html
        (new_plugin_dir / "index.html").write_text(html_content, encoding="utf-8")
        
        # Создаём ZIP архив для новой версии
        import zipfile
        zip_path = self.plugins_dir / plugin.plugin_id / f"{plugin.plugin_id}-{new_version}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(new_plugin_dir / "index.html", "index.html")
            if new_manifest_path.exists():
                zip_file.write(new_manifest_path, "manifest.json")
        
        # Обновляем версию в БД
        await self.repo.update_version(plugin_id, new_version)
        
        logger.info(f"Plugin updated successfully: plugin_id={plugin.plugin_id}, version: {old_version} -> {new_version}")
        
        return {
            "id": str(plugin.id),
            "plugin_id": plugin.plugin_id,
            "name": plugin.name,
            "old_version": old_version,
            "version": new_version,
            "is_published": plugin.is_published,
            "updated": True,
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
            import re
            import logging
            logger = logging.getLogger(__name__)

            def _to_int(x):
                if x is None:
                    return None
                try:
                    return int(x)
                except (TypeError, ValueError):
                    return None

            user_a = _to_int(user_answer.get("a"))
            user_b = _to_int(user_answer.get("b"))
            user_sum = _to_int(user_answer.get("answer"))
            question_text = (user_answer.get("question") or "").strip()

            logger.info(f"Drag-drop check: a={user_a}, b={user_b}, sum={user_sum}, question={question_text!r}")

            # Правильный ответ (сумма) — из строки "X + Y = Z" или "Решите: ? + ? = Z"
            correct_sum = None
            match = re.search(r'=\s*(\d+)\s*$', question_text)
            if match:
                correct_sum = int(match.group(1))
            if correct_sum is None:
                match_full = re.match(r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)', question_text)
                if match_full:
                    correct_sum = int(match_full.group(3))

            if correct_sum is None:
                return {
                    "correct": False,
                    "score": 0.0,
                    "explanation": f"Не удалось распознать правильный ответ из вопроса: {question_text!r}. a={user_a}, b={user_b}",
                }

            if user_a is None or user_b is None:
                return {
                    "correct": False,
                    "score": 0.0,
                    "explanation": f"Не получены оба слагаемых. Получено: a={user_a}, b={user_b}",
                }

            calculated_sum = user_a + user_b
            is_correct = calculated_sum == correct_sum
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
        
        # Логируем для диагностики
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Plugin evaluate_answer: plugin_id={plugin_id}, user_answer type={type(user_answer)}, user_answer={user_answer}")
        
        # Проверяем, является ли это TSX плагином
        # TSX плагины могут иметь plugin_id, который начинается с "tsx-" или содержит "tsx"
        # Также проверяем по имени плагина в БД и по структуре ответа
        is_tsx_plugin = plugin_id.startswith("tsx-") or "tsx" in plugin_id.lower()
        
        # Дополнительная проверка: получаем плагин из БД и проверяем его имя
        if not is_tsx_plugin:
            try:
                plugin_db = await self.repo.get_by_plugin_id(plugin_id)
                if plugin_db:
                    # Проверяем имя плагина и manifest
                    plugin_name_lower = (plugin_db.name or "").lower()
                    manifest_name_lower = ((plugin_db.manifest_data or {}).get("name", "") or "").lower()
                    if "tsx" in plugin_name_lower or "tsx" in manifest_name_lower:
                        is_tsx_plugin = True
                        logger.info(f"TSX plugin detected by name: plugin_id={plugin_id}, name={plugin_db.name}")
            except Exception as e:
                logger.warning(f"Error checking plugin in DB: {e}")
        
        # Также проверяем структуру ответа - TSX плагины отправляют isCorrect
        if not is_tsx_plugin and isinstance(user_answer, dict):
            if "isCorrect" in user_answer or "is_correct" in user_answer:
                is_tsx_plugin = True
                logger.info(f"TSX plugin detected by answer structure: plugin_id={plugin_id}, has isCorrect={('isCorrect' in user_answer)}")
        
        if is_tsx_plugin:
            # TSX плагины отправляют ответ в формате:
            # { "isCorrect": true/false, "userAnswer": "...", "correctAnswer": "..." }
            is_correct_raw = user_answer.get("isCorrect")
            user_answer_value = user_answer.get("userAnswer", "")
            correct_answer_value = user_answer.get("correctAnswer", "")
            
            # Преобразуем в булево значение
            if isinstance(is_correct_raw, bool):
                is_correct = is_correct_raw
            elif isinstance(is_correct_raw, str):
                is_correct = is_correct_raw.lower() in ("true", "1", "yes")
            elif isinstance(is_correct_raw, (int, float)):
                is_correct = bool(is_correct_raw)
            else:
                is_correct = False
                logger.warning(f"TSX plugin: isCorrect is not a valid boolean: {is_correct_raw} (type: {type(is_correct_raw)})")
            
            logger.info(f"TSX plugin answer: isCorrect={is_correct} (raw: {is_correct_raw}, type: {type(is_correct_raw)}), userAnswer={user_answer_value}, correctAnswer={correct_answer_value}")
            
            score = 1.0 if is_correct else 0.0
            
            if is_correct:
                explanation = f"Правильно! Правильный ответ: {correct_answer_value}"
            else:
                explanation = f"Неправильно. Ваш ответ: {user_answer_value}. Правильный ответ: {correct_answer_value}"
            
            return {
                "correct": is_correct,
                "score": score,
                "explanation": explanation,
                "correct_answer": correct_answer_value,  # Добавляем для отображения на фронтенде
            }
        
        # Для плагинов, которые отправляют уже проверенный ответ (с полем isCorrect)
        if "isCorrect" in user_answer or user_answer.get("isCorrect") is not None:
            is_correct_raw = user_answer.get("isCorrect")
            # Проверяем разные варианты ключей
            correct_answer_value = user_answer.get("correctAnswer") or user_answer.get("correct_answer", "")
            user_answer_value = user_answer.get("userAnswer") or user_answer.get("user_answer", "")
            
            # Преобразуем в булево значение
            if isinstance(is_correct_raw, bool):
                is_correct = is_correct_raw
            elif isinstance(is_correct_raw, str):
                is_correct = is_correct_raw.lower() in ("true", "1", "yes")
            elif isinstance(is_correct_raw, (int, float)):
                is_correct = bool(is_correct_raw)
            else:
                is_correct = False
                logger.warning(f"Plugin with isCorrect: isCorrect is not a valid boolean: {is_correct_raw} (type: {type(is_correct_raw)})")
            
            logger.info(f"Plugin with isCorrect: isCorrect={is_correct} (raw: {is_correct_raw}, type: {type(is_correct_raw)}), userAnswer={user_answer_value}, correctAnswer={correct_answer_value}")
            
            score = 1.0 if is_correct else 0.0
            
            if is_correct:
                explanation = f"Правильно! Правильный ответ: {correct_answer_value}"
            else:
                explanation = f"Неправильно. Ваш ответ: {user_answer_value}. Правильный ответ: {correct_answer_value}"
            
            return {
                "correct": is_correct,
                "score": score,
                "explanation": explanation,
                "correct_answer": correct_answer_value,
            }
        
        # Для других плагинов - базовая проверка
        # В будущем можно добавить специфичную логику для каждого плагина
        return {
            "correct": False,
            "score": 0.0,
            "explanation": "Логика проверки для этого плагина еще не реализована",
        }
