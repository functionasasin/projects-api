from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError

from src.helpers.response_helper import create_error_response

from .enums import ErrorCodes, HTTPStatusCodes


async def http_exception_handler(request: Request, exc: HTTPException):
    return create_error_response(
        error_code="HTTP_ERROR",
        message=exc.detail,
        details=None,
        status_code=exc.status_code,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return create_error_response(
        error_code=ErrorCodes.VALIDATION_ERROR.value,
        message="Validation error",
        details=exc.errors(),
        status_code=HTTPStatusCodes.UNPROCESSABLE_ENTITY.value,
    )


async def general_exception_handler(request: Request, exc: Exception):
    return create_error_response(
        error_code="SERVER_ERROR",
        message="An unexpected error occurred",
        details=str(exc),
        status_code=HTTPStatusCodes.INTERNAL_SERVER_ERROR.value,
    )


async def invalid_id_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        details=None,
        status_code=exc.status_code,
    )


async def resource_not_found_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        details=None,
        status_code=exc.status_code,
    )


async def empty_content_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        details=None,
        status_code=exc.status_code,
    )


async def project_access_denied_exception_handler(request: Request, exc):
    return create_error_response(
        error_code=exc.error_code,
        message=exc.detail,
        details=None,
        status_code=exc.status_code,
    )
