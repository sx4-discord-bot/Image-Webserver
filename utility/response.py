import json

from flask import Response


class JsonResponse(Response):

    def __init__(self, status: int, message: str):
        super().__init__()

        self.status_code = status
        self.data = json.dumps({"status": status, "message": message})
        self.content_type = "application/json"


class BadRequest(JsonResponse):

    def __init__(self, message: str=None):
        super().__init__(400, message)


class Unauthorized(JsonResponse):

    def __init__(self, message: str=None):
        super().__init__(401, message)


class Forbidden(JsonResponse):

    def __init__(self, message: str=None):
        super().__init__(403, message)


class NotFound(JsonResponse):

    def __init__(self, message: str=None):
        super().__init__(404, message)


class InternalError(JsonResponse):

    def __init__(self, message: str=None):
        super().__init__(500, message)
