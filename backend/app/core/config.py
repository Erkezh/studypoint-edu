from __future__ import annotations

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "IXL Clone API"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"

    database_url: str
    redis_url: str

    jwt_issuer: str = "ixl-clone"
    jwt_audience: str = "ixl-clone-users"
    jwt_secret_key: str
    jwt_access_ttl_sec: int = 900
    jwt_refresh_ttl_sec: int = 60 * 60 * 24 * 30

    password_hash_scheme: str = "argon2"

    cache_ttl_sec: int = 60

    auth_rate_limit: int = 10
    auth_rate_window_sec: int = 60
    submit_rate_limit: int = 30
    submit_rate_window_sec: int = 60

    free_daily_question_limit: int = 25

    practice_stop_smartscore: int = 90
    practice_stop_min_questions: int = 10
    practice_session_expiry_hours: int = 24

    # Plugin settings
    plugins_dir: str = "static/plugins"  # Директория для хранения плагинов
    plugin_max_size_mb: int = 10  # Максимальный размер ZIP плагина


settings = Settings()  # type: ignore[call-arg]
