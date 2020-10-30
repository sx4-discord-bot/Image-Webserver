import colorsys
from typing import Optional

from handlers.handler import SingleImageHandler
from utility.image import max_pixels, get_image_response
from utility.response import BadRequest


class HueHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["image"], str), (["frames"], Optional[int])]

    def on_request(self, image):
        frame_count = self.query("frames", int) or 60
        if frame_count > 100:
            raise BadRequest("Frame count cannot be more than 100")

        final_size = max_pixels(image.size, 100)
        image = image.convert("RGBA").resize(final_size)

        frames = []
        for i in range(0, frame_count):
            copy = image.copy()
            pixels = copy.load()
            for x in range(0, image.size[0]):
                for y in range(0, image.size[1]):
                    r, g, b, a = pixels[x, y]

                    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                    nr, ng, nb = colorsys.hsv_to_rgb(((h * 360 + i * 360 / frame_count) % 360) / 360, s, v)

                    pixels[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)

            frames.append(copy)

        return get_image_response(frames, transparency=255)
