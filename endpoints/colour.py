from typing import Optional

from PIL import Image

from handlers.handler import GetHandler
from utility.colour import as_rgb_tuple
from utility.image import get_image_response
from utility.response import BadRequest


class ColourHandler(GetHandler):

    def __init__(self, app):
        super().__init__(app)

        self.aliases = ["color"]
        self.queries = [(["width", "w"], Optional[int]), (["height", "h"], Optional[int])]

    def on_request(self):
        colour = self.query("colour", int)
        if not colour:
            raise BadRequest("colour query not given or not valid")

        width = self.query("width", int) or self.query("w", int) or 100
        height = self.query("height", int) or self.query("h", int) or 100

        return get_image_response([Image.new("RGB", (width, height), as_rgb_tuple(colour))])
