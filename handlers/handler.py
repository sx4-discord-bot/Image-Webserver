from typing import Any, Type

from PIL import UnidentifiedImageError
from flask import Response, request
from requests.exceptions import MissingSchema, ConnectionError

from utility.image import get_image
from utility.response import BadRequest


class Handler:

    def __init__(self, app):
        self.request = request
        self.app = app
        self.aliases = []
        self.queries = []
        self.bodies = []
        self.name = self.__module__.split(".")[-1]  # -1 in case the root of the file changes

    def __call__(self):
        return self.on_request()

    def on_request(self, *args):
        return Response(status=204)

    def query(self, query: str, type: Type[Any] = str) -> Any:
        return self.request.args.get(query, type=type)

    def header(self, header: str, type: Type[Any] = str) -> Any:
        return self.request.headers.get(header, type=type)

    def body(self, key: str, type: Type[Any] = str) -> Any:
        return self.request.json.get(key, type=type)


class GetHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["GET"]


class PostHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["POST"]


class SingleImageHandler(GetHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["image"], str)]

    def __call__(self):
        image_url = self.query("image")
        if not image_url:
            return BadRequest("Image query not given")

        try:
            image = get_image(image_url)
        except MissingSchema:
            return BadRequest("Invalid url")
        except UnidentifiedImageError:
            return BadRequest("Url could not be formed to an image")
        except ConnectionError:
            return BadRequest("Site took too long to respond")

        return self.on_request(image)

    def on_request(self, image):
        pass
