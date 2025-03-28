from enum import Enum

class HTTPStatusCodes(Enum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500

class ErrorCodes(Enum):
    INVALID_CREDENTIALS = "InvalidCredentials"
    RESOURCE_NOT_FOUND = "ResourceNotFound"
    USER_ALREADY_EXISTS = "UserAlreadyExists"
    VALIDATION_ERROR = "ValidationError"
    UNAUTHORIZED_ACCESS = "UnauthorizedAccess"
    EMPTY_CONTENT = "EmptyContent"
    INVALID_ID = "InvalidID"
    PROJECT_ACCESS_DENIED = "ProjectAccessDenied" 