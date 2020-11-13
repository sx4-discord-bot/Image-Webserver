import json
from functools import wraps
from typing import Any, Type, List, Tuple

from PIL import Image
from flask import request

from utility.image import get_image, get_image_response, for_each_frame
from utility.response import BadRequest, Unauthorized

config = json.load(open("config.json"))


def check_names(t, names, queries, name_type):
    if hasattr(t, "__args__"):
        args = t.__args__
        if len(args) == 2 and args[1] is type(None):
            return

    for name in names:
        if name in queries:
            return

        raise BadRequest(f"{name} is not given as a {name_type}")


def check_authorization(f):
    @wraps(f)
    def wrapper(self):
        if not self.require_authorization:
            return f(self)

        authorization = request.headers.get("authorization")
        if not authorization:
            raise Unauthorized("Authorization header not given")

        if authorization != self.config["auth"]:
            raise Unauthorized("Invalid authorization header")

        return f(self)

    return wrapper


def check_queries(f):
    @wraps(f)
    def wrapper(self):
        queries = [k for k, v in self.request.args.items()]
        for names, t in self.queries:
            check_names(t, names, queries, "query")

        return f(self)

    return wrapper


def check_fields(f):
    @wraps(f)
    def wrapper(self):
        if len(self.fields) == 0:
            return f(self)

        if not self.request.is_json:
            raise BadRequest("Body has to be json")

        fields = [k for k, v in self.request.json.items()]
        for names, t in self.fields:
            check_names(t, names, fields, "field")

        return f(self)

    return wrapper


class Handler:

    def __init__(self, app):
        self.request = request
        self.methods = ["GET"]
        self.app = app
        self.config = config
        self.require_authorization = True
        self.aliases = []
        self.queries = []
        self.fields = []
        self.name = self.__module__.split(".")[-1]  # -1 in case the root of the file changes

    @check_authorization
    @check_fields
    @check_queries
    def __call__(self):
        return self.on_request()

    def on_request(self, *args):
        pass

    def query(self, query: str, type: [Any] = str, default: Any = None) -> Any:
        return self.request.args.get(query, type=type, default=default)

    def header(self, header: str, type: Type[Any] = str, default: Any = None) -> Any:
        return self.request.headers.get(header, type=type, default=default)

    def body(self, key: str, type: Type[Any] = str, default: Any = None) -> Any:
        try:
            return type(self.request.json.get(key, default))
        except ValueError:
            raise BadRequest(f"{key} is meant to be a {type.__name__}")


class MultipleImageHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.fields += [([k], str) for k, v in self.image_queries() if v]
        self.queries += [([k], str) for k, v in self.image_queries() if not v]

    @check_authorization
    @check_fields
    @check_queries
    def __call__(self):
        images = []
        for name, is_body in self.image_queries():
            name_type = "field" if is_body else "query"
            query = self.body(name) if is_body else self.query(name)

            images.append(get_image(query, name, name_type))

        return self.on_request(self.modify_images(images))

    def on_request(self, images: List[type(Image)]):
        pass

    def image_queries(self) -> List[Tuple[str, bool]]:
        pass

    def modify_images(self, images: List[type(Image)]) -> Any:
        return images


class SingleImageHandler(MultipleImageHandler):

    def on_request(self, image: Image):
        pass

    def image_queries(self):
        return [("image", False)]

    def modify_images(self, images: List[type(Image)]) -> Any:
        return images[0]


class ImageFilterHandler(SingleImageHandler):

    def on_request(self, image):
        filter = self.filter()

        frames = for_each_frame(image, lambda frame: frame.convert("RGBA").filter(filter))

        return get_image_response(frames, transparency=255)

    def filter(self):
        pass
