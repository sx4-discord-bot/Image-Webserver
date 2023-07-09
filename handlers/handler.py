from functools import wraps
from io import BytesIO
from typing import Any, Type, List, Tuple, Optional

from PIL import Image, UnidentifiedImageError
from flask import request

from utility.config import config
from utility.error import ErrorCode
from utility.image import get_image, get_image_response, for_each_frame
from utility.response import BadRequest, Unauthorized, MethodNotAllowed


def check_names(t, names, queries, field):
    if hasattr(t, "__args__"):
        args = t.__args__
        if len(args) == 2 and args[1] is type(None):
            return

    for name in names:
        if name in queries:
            return

    error_code = ErrorCode.FIELD_MISSING if field else ErrorCode.QUERY_MISSING
    raise BadRequest(f"{names[0]} is not given as a {'field' if field else 'query'}", error_code)


def check_authorization(f):
    @wraps(f)
    def wrapper(self):
        if not self.require_authorization:
            return f(self)

        authorization = request.headers.get("authorization")
        if not authorization:
            raise Unauthorized("Authorization header not given")

        auth = config.get("auth")
        for key in auth:
            if auth[key] == authorization:
                self.authorization_type = key
                return f(self)

        raise Unauthorized("Invalid authorization header")

    return wrapper


def check_queries(f):
    @wraps(f)
    def wrapper(self):
        queries = [k for k, v in self.request.args.items()]
        for names, t in self.queries:
            check_names(t, names, queries, False)

        return f(self)

    return wrapper


def check_fields(f):
    @wraps(f)
    def wrapper(self):
        if len(self.fields) == 0:
            return f(self)

        if not self.request.is_json:
            raise BadRequest("Body has to be valid json", ErrorCode.INVALID_BODY_JSON)

        fields = [k for k, v in self.request.json.items()]
        for names, t in self.fields:
            check_names(t, names, fields, True)

        return f(self)

    return wrapper


class Handler:

    def __init__(self, app):
        self.request = request
        self.methods = ["GET"]
        self.app = app
        self.require_authorization = True
        self.authorization_type = None
        self.aliases = []
        self.queries = []
        self.fields = []
        self.name = self.__module__.split(".")[-1]

    @check_authorization
    @check_fields
    @check_queries
    def __call__(self):
        return self.on_request()

    def on_request(self, *args):
        pass

    def query(self, query: str, type: Type[Any] = str, default: Any = None) -> Any:
        return self.request.args.get(query, type=type, default=default)

    def header(self, header: str, type: Type[Any] = str, default: Any = None) -> Any:
        return self.request.headers.get(header, type=type, default=default)

    def body(self, key: str, type: Optional[Type[Any]] = str, default: Any = None) -> Any:
        value = self.request.json.get(key)
        if value is None:
            return default

        if not type:
            return value

        try:
            return type(value)
        except ValueError:
            raise BadRequest(f"{key} is meant to be a {type.__name__}", ErrorCode.INVALID_QUERY_VALUE)


class MultipleImageHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.fields += [([k], str if r else Optional[str]) for k, v, r in self.image_queries() if v]
        self.queries += [([k], str if r else Optional[str]) for k, v, r in self.image_queries() if not v]

    @check_authorization
    @check_fields
    @check_queries
    def __call__(self):
        images = []
        for name, body, _ in self.image_queries():
            name_type = "field" if body else "query"
            query = self.body(name) if body else self.query(name)

            images.append(get_image(query, name, name_type))

        return self.on_request(self.modify_images(images))

    def on_request(self, images: List[type(Image)]):
        pass

    def image_queries(self) -> List[Tuple[str, bool, bool]]:
        pass

    def modify_images(self, images: List[type(Image)]) -> Any:
        return images


class SingleImageHandler(MultipleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["GET", "POST"]

    @check_authorization
    @check_fields
    @check_queries
    def __call__(self):
        name, body, _ = self.image_queries()[0]
        name_type = "field" if body else "query"
        query = self.body(name) if body else self.query(name)

        if query and not body and self.request.method != "GET":
            raise MethodNotAllowed("Use GET when providing the image as a query")

        image = None
        if not query and len(self.fields) == 0:
            if self.request.method != "POST":
                raise MethodNotAllowed("Use POST when providing the image in the body")

            data = self.request.data
            if not isinstance(data, bytes):
                raise BadRequest("Body is meant to be bytes", ErrorCode.INVALID_BODY_BYTES)

            try:
                image = Image.open(BytesIO(data))
            except UnidentifiedImageError:
                raise BadRequest("Could not resolve body to an image", ErrorCode.INVALID_IMAGE_BYTES)
        elif query:
            image = get_image(query, name, name_type)

        if not image:
            raise BadRequest("Image not given in query or body", ErrorCode.VALUE_MISSING)

        return self.on_request(self.modify_images([image]))

    def on_request(self, image: Image):
        pass

    def image_queries(self):
        return [("image", False, False)]

    def modify_images(self, images: List[type(Image)]) -> Any:
        return images[0]


class ImageFilterHandler(SingleImageHandler):

    def on_request(self, image):
        filter = self.filter()

        frames = for_each_frame(image, lambda frame: frame.convert("RGBA").filter(filter))

        return get_image_response(frames, transparency=255)

    def filter(self):
        pass
