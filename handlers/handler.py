from typing import Any, Type, List

from PIL import UnidentifiedImageError, Image
from flask import Response, request
from requests.exceptions import MissingSchema, ConnectionError

from utility.image import get_image, get_image_response, for_each_frame
from utility.response import BadRequest


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


class MultipleImageHandler(GetHandler):

    def __call__(self):
        images = []
        for name in self.image_queries():
            query = self.query(name)
            if not query:
                return BadRequest(f"{name} query not given")

            try:
                image = get_image(query)
            except MissingSchema:
                return BadRequest(f"Invalid url given for {name}")
            except UnidentifiedImageError:
                return BadRequest(f"{name} could not be formed to an image")
            except ConnectionError:
                return BadRequest(f"Site took too long to respond for {name}")

            images.append(image)

        return self.on_request(self.modify_images(images))

    def on_request(self, images: List[type(Image)]):
        pass

    def image_queries(self) -> List[str]:
        pass

    def modify_images(self, images: List[type(Image)]) -> Any:
        return images


class SingleImageHandler(MultipleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["image"], str)]

    def on_request(self, image: Image):
        pass

    def image_queries(self):
        return ["image"]

    def modify_images(self, images: List[type(Image)]) -> Any:
        return images[0]


class ImageFilterHandler(SingleImageHandler):

    def on_request(self, image):
        filter = self.filter()

        frames = for_each_frame(image, lambda frame: frame.convert("RGBA").filter(filter))

        return get_image_response(frames, transparency=255)

    def filter(self):
        pass
