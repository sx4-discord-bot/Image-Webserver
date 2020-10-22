from flask import Response, request


class Handler:

    def __init__(self):
        self.request = request

    def __call__(self, *args):
        return Response(status=204)

    def query(self, query: str):
        return self.request.args.get(query)
