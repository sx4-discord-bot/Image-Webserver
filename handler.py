from typing import Any

from flask import Response, request


class Handler:

    def __init__(self):
        self.request = request

    def __call__(self):
        return Response(status=204)

    def query(self, query: str) -> str:
        return self.request.args.get(query)

    def header(self, header: str) -> Any:
        return self.request.headers.get(header)
