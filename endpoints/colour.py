from typing import Optional

from PIL import Image

from handlers.handler import Handler
from utility.colour import as_rgb_tuple
from utility.image import get_image_response


class ColourHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.aliases = ["color"]
        self.queries = [(["width", "w"], Optional[int]), (["height", "h"], Optional[int]), (["colour", "color"], int)]

    def on_request(self):
        colour = self.query("colour", int, 0) or self.query("color", int, 0)

        width = self.query("width", int) or self.query("w", int) or 100
        height = self.query("height", int) or self.query("h", int) or 100

        return get_image_response([Image.new("RGB", (width, height), as_rgb_tuple(colour))])
