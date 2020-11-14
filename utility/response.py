import json

from flask import Response


class JsonException(Exception):

    def __init__(self, status: int, message: str, extra: dict = None):
        super().__init__()

        data = {"status": status}

        if message:
            data["message"] = message

        if extra:
            data.update(extra)

        self.status_code = status
        self.data = json.dumps(data)
        self.content_type = "application/json"

    def as_response(self):
        return Response(status=self.status_code, response=self.data, content_type=self.content_type)


class BadRequest(JsonException):

    def __init__(self, message: str = None, extra: dict = None):
        super().__init__(400, message, extra)


class Unauthorized(JsonException):

    def __init__(self, message: str = None, extra: dict = None):
        super().__init__(401, message, extra)


class Forbidden(JsonException):

    def __init__(self, message: str = None, extra: dict = None):
        super().__init__(403, message, extra)


class NotFound(JsonException):

    def __init__(self, message: str = None, extra: dict = None):
        super().__init__(404, message, extra)


class MethodNotAllowed(JsonException):

    def __init__(self, message: str = None, extra: dict = None):
        super().__init__(405, message, extra)


class InternalError(JsonException):

    def __init__(self, message: str = None, extra: dict = None):
        super().__init__(500, message, extra)
