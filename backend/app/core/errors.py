from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorDetail(BaseModel):
    loc: list[str] | None = None
    msg: str | None = None
    type: str | None = None


class ErrorBody(BaseModel):
    code: str = Field(examples=["validation_error", "unauthorized", "not_found"])
    message: str = Field(examples=["Invalid request"])
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                error=ErrorBody(
                    code="validation_error",
                    message="Request validation error",
                    details=exc.errors(),
                )
            ).model_dump(mode="json"),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorBody(code="http_error", message=str(exc.detail), details=None)
            ).model_dump(mode="json"),
        )

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=ErrorBody(code=exc.code, message=exc.message, details=exc.details)
            ).model_dump(mode="json"),
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_request: Request, exc: Exception):
        import traceback
        import logging
        
        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        # Для SQLAlchemy ошибок возвращаем более понятное сообщение
        error_message = "Internal server error"
        error_details = None
        
        if "IntegrityError" in str(type(exc)) or "ForeignKeyViolationError" in str(exc):
            if "foreign key constraint" in str(exc).lower():
                error_message = "Referenced resource not found (foreign key violation)"
                if "skill_id" in str(exc):
                    error_details = "The specified skill_id does not exist in the database"
            elif "unique constraint" in str(exc).lower():
                error_message = "Resource already exists (unique constraint violation)"
        elif "DBAPIError" in str(type(exc)):
            if "enum" in str(exc).lower():
                error_message = "Invalid enum value"
                error_details = str(exc)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error=ErrorBody(
                    code="internal_error",
                    message=error_message,
                    details=error_details
                )
            ).model_dump(mode="json"),
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
