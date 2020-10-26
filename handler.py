from typing import Any, Type

from flask import Response, request


class Handler:

    def __init__(self, app):
        self.request = request
        self.app = app
        self.aliases = []
        self.queries = []
        self.name = self.__module__.split(".")[1]

    def __call__(self):
        return Response(status=204)

    def query(self, query: str, type: Type[Any] = str) -> Any:
        return self.request.args.get(query, type=type)

    def header(self, header: str, type: Type[Any] = str) -> Any:
        return self.request.headers.get(header, type=type)
