from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import TypeVar, Optional, Any
from src.models.response_model import SuccessResponse, ErrorResponse
from src.core import HTTPStatusCodes

T = TypeVar('T')

def create_success_response(
    data: Optional[T] = None,
    message: str = "Operation successful",
    status_code: int = HTTPStatusCodes.OK.value,
) -> JSONResponse:
    response = SuccessResponse[T](message=message, data=data)
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response)
    )

def create_error_response(
    error_code: str,
    message: str = "An error occurred",
    details: Optional[Any] = None,
    status_code: int = HTTPStatusCodes.BAD_REQUEST.value,
) -> JSONResponse:
    response = ErrorResponse(error=error_code, message=message, details=details)
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(response)
    ) 