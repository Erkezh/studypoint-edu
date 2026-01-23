from __future__ import annotations

import re
import zipfile
from pathlib import Path


class PluginSecurityError(Exception):
    """Ошибка безопасности при проверке плагина."""
    pass


def scan_zip_contents(zip_path: Path, max_size_mb: int = 10) -> None:
    """Проверяет содержимое ZIP-архива на безопасность.
    
    Проверяет:
    - Размер архива не превышает лимит
    - Нет опасных файлов (executable, .py, .js с eval)
    - Нет путей выхода за пределы директории (zip slip)
    - Нет удаленных скриптов (remote script src)
    
    Raises:
        PluginSecurityError: если обнаружены проблемы безопасности
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    # Проверка размера файла
    if zip_path.stat().st_size > max_size_bytes:
        raise PluginSecurityError(f"ZIP файл слишком большой (максимум {max_size_mb}MB)")
    
    # Опасные паттерны в именах файлов
    dangerous_patterns = [
        r"\.py$",
        r"\.pyc$",
        r"\.exe$",
        r"\.sh$",
        r"\.bat$",
        r"\.cmd$",
    ]
    
    # Опасные паттерны в содержимом (для текстовых файлов)
    dangerous_content_patterns = [
        r"eval\s*\(",
        r"new\s+Function\s*\(",
        r"Function\s*\(",
        r"<script[^>]*src\s*=\s*['\"]https?://",  # Remote script src
        r"<iframe[^>]*src\s*=\s*['\"]https?://",  # Remote iframe
    ]
    
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            # Проверка на zip slip (пути выхода за пределы)
            for member in zip_file.namelist():
                # Нормализуем путь и проверяем, что он не выходит за пределы
                normalized = Path(member).resolve()
                if not str(normalized).startswith(str(zip_path.parent.resolve())):
                    # Это не zip slip, но проверяем относительный путь
                    if ".." in member or member.startswith("/"):
                        raise PluginSecurityError(f"Небезопасный путь в архиве: {member}")
                
                # Проверка расширения файла
                for pattern in dangerous_patterns:
                    if re.search(pattern, member, re.IGNORECASE):
                        raise PluginSecurityError(f"Запрещенный тип файла: {member}")
                
                # Проверка содержимого текстовых файлов
                if member.endswith((".html", ".js", ".json")):
                    try:
                        content = zip_file.read(member).decode("utf-8", errors="ignore")
                        for pattern in dangerous_content_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                raise PluginSecurityError(
                                    f"Обнаружен опасный код в {member}: {pattern}"
                                )
                    except (UnicodeDecodeError, zipfile.BadZipFile):
                        # Пропускаем бинарные файлы или поврежденные
                        pass
                        
    except zipfile.BadZipFile:
        raise PluginSecurityError("Некорректный ZIP файл")
    except Exception as e:
        if isinstance(e, PluginSecurityError):
            raise
        raise PluginSecurityError(f"Ошибка при проверке архива: {str(e)}")
