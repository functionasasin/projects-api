from enum import Enum


class HTTPStatusCodes(Enum):
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


class ErrorCodes(Enum):
    RESOURCE_NOT_FOUND = "ResourceNotFound"
    VALIDATION_ERROR = "ValidationError"
    EMPTY_CONTENT = "EmptyContent"
    INVALID_ID = "InvalidID"
    PROJECT_ACCESS_DENIED = "ProjectAccessDenied"
