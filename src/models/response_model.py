from pydantic import BaseModel, Field
from typing import Any, Optional, Generic, TypeVar, Dict, List, Union

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    status: str = Field(default="Success", examples=["Success"])
    message: str = Field(..., examples=["Operation completed successfully"])
    data: Optional[T] = None
    
    model_config = {}

class ErrorResponse(BaseModel):
    status: str = Field(default="Error", examples=["Error"])
    error: str = Field(..., examples=["NOT_FOUND"])
    message: str = Field(..., examples=["Resource not found"])
    details: Optional[Any] = None
    
    model_config = {} 