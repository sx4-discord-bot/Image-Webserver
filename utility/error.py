from enum import Enum


class ErrorType:

    def __init__(self, code: int, reason: str):
        self.code = code
        self.reason = reason

    def __str__(self):
        return self.reason

    def __int__(self):
        return self.code

    def as_json(self):
        return {"details": {"code": self.code, "reason": self.reason}}


class ErrorCode(Enum):
    INVALID_URL = ErrorType(0, "Argument could not be formed to a proper url")
    INVALID_IMAGE_URL = ErrorType(1, "Url could not be formed to a proper image")
    URL_TIMEOUT = ErrorType(2, "Timed out while trying to get content from url")
    INVALID_BODY_JSON = ErrorType(3, "Body was not valid json")
    FIELD_MISSING = ErrorType(4, "Required field was missing from body")
    INVALID_FIELD_VALUE = ErrorType(5, "A field given was an invalid value")
    QUERY_MISSING = ErrorType(6, "Required query was missing from url")
    INVALID_QUERY_VALUE = ErrorType(7, "A query given was an invalid value")
    INVALID_BODY_BYTES = ErrorType(8, "Body was not valid bytes")
    INVALID_IMAGE_BYTES = ErrorType(9, "Body bytes could not be formed to a proper image")
    VALUE_MISSING = ErrorType(10, "A value is missing from the queries, fields or body")

