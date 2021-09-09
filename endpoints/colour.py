from typing import Optional

from PIL import Image

from handlers.handler import Handler
from utility.colour import as_rgb_tuple
from utility.error import ErrorCode
from utility.image import get_image_response
from utility.response import BadRequest


class ColourHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.aliases = ["color"]
        self.queries = [(["width", "w"], Optional[int]), (["height", "h"], Optional[int]), (["colour", "color"], int)]
        self.require_authorization = False

    def on_request(self):
        colour = self.query("colour", int, 0) or self.query("color", int, 0)

        width = self.query("width", int) or self.query("w", int) or 100
        height = self.query("height", int) or self.query("h", int) or 100

        if width > 5000 or height > 5000:
            raise BadRequest("Neither width or height can be more than 5000 pixels in size", ErrorCode.INVALID_QUERY_VALUE)

        return get_image_response([Image.new("RGB", (width, height), as_rgb_tuple(colour))])
