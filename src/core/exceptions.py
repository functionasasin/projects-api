from fastapi import HTTPException
from .enums import HTTPStatusCodes, ErrorCodes

# Authentication-related exceptions - not currently used
# class InvalidCredentialsException(HTTPException):
#     def __init__(self, message="Incorrect username or password"):
#         super().__init__(
#             status_code=HTTPStatusCodes.UNAUTHORIZED.value,
#             detail=message,
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#         self.error_code = ErrorCodes.INVALID_CREDENTIALS.value

# class UserAlreadyExistsException(HTTPException):
#     def __init__(self, message="User already exists"):
#         super().__init__(
#             status_code=HTTPStatusCodes.CONFLICT.value,
#             detail=message,
#         )
#         self.error_code = ErrorCodes.USER_ALREADY_EXISTS.value

# class UnauthorizedAccessException(HTTPException):
#     def __init__(self, message="Unauthorized access"):
#         super().__init__(
#             status_code=HTTPStatusCodes.UNAUTHORIZED.value,
#             detail=message,
#         )
#         self.error_code = ErrorCodes.UNAUTHORIZED_ACCESS.value

class ResourceNotFoundException(HTTPException):
    def __init__(self, resource_name="Resource", message="Resource not found"):
        super().__init__(
            status_code=HTTPStatusCodes.NOT_FOUND.value,
            detail=f"{resource_name} not found" if message == "Resource not found" else message,
        )
        self.error_code = ErrorCodes.RESOURCE_NOT_FOUND.value

class EmptyContentException(HTTPException):
    def __init__(self, message="Content cannot be empty"):
        super().__init__(
            status_code=HTTPStatusCodes.BAD_REQUEST.value,
            detail=message,
        )
        self.error_code = ErrorCodes.EMPTY_CONTENT.value

class InvalidIDException(HTTPException):
    def __init__(self, message="Invalid ID format"):
        super().__init__(
            status_code=HTTPStatusCodes.BAD_REQUEST.value,
            detail=message,
        )
        self.error_code = ErrorCodes.INVALID_ID.value

class ProjectAccessDeniedException(HTTPException):
    def __init__(self, message="You don't have access to this project"):
        super().__init__(
            status_code=HTTPStatusCodes.FORBIDDEN.value,
            detail=message,
        )
        self.error_code = ErrorCodes.PROJECT_ACCESS_DENIED.value 