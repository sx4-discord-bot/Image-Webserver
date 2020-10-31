from functools import wraps
from typing import Any, Type, List, Tuple

from PIL import UnidentifiedImageError, Image
from flask import Response, request
from requests.exceptions import MissingSchema, ConnectionError

from utility.image import get_image, get_image_response, for_each_frame
from utility.response import BadRequest

def check_queries(f):
    def check_names(t, names, queries):
        for name in names:
            if hasattr(t, "__args__"):
                args = t.__args__
                if len(args) == 2 and args[1] is type(None):
                    return

            if name not in queries:
                raise BadRequest(f"{name} is not given as a query")

    @wraps(f)
    def wrapper(self):
        queries = [k for k, v in self.request.args.items()]
        for names, t in self.queries:
            check_names(t, names, queries)

        return f(self)

    return wrapper


def check_fields(f):
    def check_names(t, names, fields):
        for name in names:
            if hasattr(t, "__args__"):
                args = t.__args__
                if len(args) == 2 and args[1] is type(None):
                    return

            if name not in fields:
                raise BadRequest(f"{name} is not given as a field")

    @wraps(f)
    def wrapper(self):
        if len(self.fields) == 0:
            return f(self)

        if not self.request.is_json:
            raise BadRequest("Body has to be json")

        fields = [k for k, v in self.request.json.items()]
        for names, t in self.fields:
            check_names(t, names, fields)

        return f(self)

    return wrapper


class Handler:

    def __init__(self, app):
        self.request = request
        self.app = app
        self.aliases = []
        self.queries = []
        self.fields = []
        self.name = self.__module__.split(".")[-1]  # -1 in case the root of the file changes

    def __call__(self):
        return self.on_request()

    @check_fields
    @check_queries
    def on_request(self):
        pass

    def query(self, query: str, type: Type[Any] = str, default: Any = None) -> Any:
        return self.request.args.get(query, type=type, default=default)

    def header(self, header: str, type: Type[Any] = str, default: Any = None) -> Any:
        return self.request.headers.get(header, type=type, default=default)

    def body(self, key: str, type: Type[Any] = str, default: Any = None) -> Any:
        try:
            return type(self.request.json.get(key, default))
        except ValueError:
            raise BadRequest(f"{key} is meant to be a {type.__name__}")


class GetHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["GET"]

    @check_queries
    def on_request(self):
        pass


class PostHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["POST"]

    @check_fields
    def on_request(self):
        pass


class MultipleImageHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.fields += [([k], str) for k, v in self.image_queries() if v]
        self.queries += [([k], str) for k, v in self.image_queries() if not v]

    def __call__(self):
        super().on_request()

        images = []
        for name, is_body in self.image_queries():
            name_type = "field" if is_body else "query"
            query = self.body(name) if is_body else self.query(name)
            if not query:
                raise BadRequest(f"{name} query not given")

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
