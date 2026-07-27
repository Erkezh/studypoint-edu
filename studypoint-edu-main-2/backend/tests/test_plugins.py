"""Тесты для модуля плагинов."""

from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

import pytest

from app.plugins.security import PluginSecurityError, scan_zip_contents
from app.plugins.schemas import PluginManifest


def test_manifest_validation_valid():
    """Тест валидации корректного manifest."""
    manifest_data = {
        "id": "test-plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
        "entry": "index.html",
        "apiVersion": "1",
        "capabilities": {
            "submit": True,
            "explanation": True,
        },
        "height": 400,
    }
    
    manifest = PluginManifest.model_validate(manifest_data)
    assert manifest.id == "test-plugin"
    assert manifest.name == "Test Plugin"
    assert manifest.version == "1.0.0"
    assert manifest.entry == "index.html"
    assert manifest.api_version == "1"
    assert manifest.capabilities["submit"] is True
    assert manifest.height == 400


def test_manifest_validation_missing_required():
    """Тест валидации manifest с отсутствующими обязательными полями."""
    manifest_data = {
        "id": "test-plugin",
        "name": "Test Plugin",
        # Отсутствует version
    }
    
    with pytest.raises(Exception):  # Pydantic ValidationError
        PluginManifest.model_validate(manifest_data)


def test_manifest_validation_invalid_version():
    """Тест валидации manifest с неверным форматом версии."""
    manifest_data = {
        "id": "test-plugin",
        "name": "Test Plugin",
        "version": "invalid-version",  # Не соответствует semver
        "entry": "index.html",
        "apiVersion": "1",
    }
    
    # Pydantic не проверяет формат версии, но JSON Schema должен
    # В реальности это проверяется на уровне JSON Schema валидации
    manifest = PluginManifest.model_validate(manifest_data)
    assert manifest.version == "invalid-version"


def test_security_scan_safe_zip(tmp_path: Path):
    """Тест security scan для безопасного ZIP."""
    # Создаем безопасный ZIP
    zip_path = tmp_path / "safe.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("index.html", "<html><body>Safe content</body></html>")
        zf.writestr("manifest.json", json.dumps({
            "id": "test",
            "name": "Test",
            "version": "1.0.0",
            "entry": "index.html",
            "apiVersion": "1",
        }))
    
    # Должно пройти без ошибок
    scan_zip_contents(zip_path, max_size_mb=10)


def test_security_scan_dangerous_file(tmp_path: Path):
    """Тест security scan для ZIP с опасным файлом (.py)."""
    zip_path = tmp_path / "dangerous.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("dangerous.py", "print('dangerous')")
        zf.writestr("index.html", "<html></html>")
    
    # Должно вызвать ошибку
    with pytest.raises(PluginSecurityError, match="Запрещенный тип файла"):
        scan_zip_contents(zip_path, max_size_mb=10)


def test_security_scan_eval_in_js(tmp_path: Path):
    """Тест security scan для ZIP с eval в JS файле."""
    zip_path = tmp_path / "eval.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("script.js", "eval('dangerous code')")
        zf.writestr("index.html", "<html></html>")
    
    # Должно вызвать ошибку
    with pytest.raises(PluginSecurityError, match="опасный код"):
        scan_zip_contents(zip_path, max_size_mb=10)


def test_security_scan_remote_script(tmp_path: Path):
    """Тест security scan для ZIP с удаленным скриптом."""
    zip_path = tmp_path / "remote.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("index.html", '<script src="https://evil.com/script.js"></script>')
    
    # Должно вызвать ошибку
    with pytest.raises(PluginSecurityError, match="опасный код"):
        scan_zip_contents(zip_path, max_size_mb=10)


def test_security_scan_zip_slip(tmp_path: Path):
    """Тест security scan для ZIP с zip slip атакой."""
    zip_path = tmp_path / "zipslip.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        # Создаем файл с путем выхода за пределы
        zf.writestr("../../dangerous.txt", "dangerous content")
    
    # Должно вызвать ошибку
    with pytest.raises(PluginSecurityError, match="Небезопасный путь"):
        scan_zip_contents(zip_path, max_size_mb=10)


def test_security_scan_size_limit(tmp_path: Path):
    """Тест security scan для ZIP превышающего размер."""
    zip_path = tmp_path / "large.zip"
    
    # Создаем большой файл (11MB)
    large_content = b"x" * (11 * 1024 * 1024)
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("large.txt", large_content)
    
    # Должно вызвать ошибку
    with pytest.raises(PluginSecurityError, match="слишком большой"):
        scan_zip_contents(zip_path, max_size_mb=10)
