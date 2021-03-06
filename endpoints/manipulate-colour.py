import colorsys
from io import BytesIO
from typing import Optional

from PIL import Image

from handlers.handler import Handler, SingleImageHandler
from utility.colour import as_rgb_tuple
from utility.image import get_image_response, for_each_frame, get_image


class ManipulateColourHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.aliases = ["manipulate-color"]
        self.queries += [(["colour", "color"], int)]

    def on_request(self, image):
        colour = as_rgb_tuple(self.query("colour", int, 0) or self.query("color", int, 0))

        h, s, v = colorsys.rgb_to_hsv(colour[0] / 255, colour[1] / 255, colour[2] / 255)

        def parse(frame):
            frame = frame.convert("RGBA")
            pixels = frame.load()
            for x in range(frame.size[0]):
                for y in range(frame.size[1]):
                    r, g, b, a = pixels[x, y]

                    ch, cs, cv = colorsys.rgb_to_hsv(r / 255, b / 255, g / 255)
                    nr, ng, nb = colorsys.hsv_to_rgb(h, cs, cv)

                    pixels[x, y] = int(nr * 255), int(ng * 255), int(nb * 255), a

            return frame

        return get_image_response(for_each_frame(image, parse), transparency=255)
