from math import sqrt

from PIL import ImageSequence
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.image import get_image, max_pixels, get_image_response
from utility.response import BadRequest


class HalloweenHandler(Handler):

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
            return BadRequest("Url could not be formed to an image")
        except ConnectionError:
            return BadRequest("Site took too long to respond")

        final_size = max_pixels(image.size, 500)

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize(final_size)

            pixels = frame.load()
            for x in range(0, frame.size[0]):
                for y in range(0, frame.size[1]):
                    r, g, b, a = pixels[x, y]

                    o = sqrt(r ** 2 * 0.299 + g ** 2 * 0.587 + b ** 2 * 0.114)
                    o *= (o - 102) / 128

                    pixels[x, y] = (min(max(int(o), 0), 255), min(max(int((o - 10) / 2), 0), 255), 0, a)

            frames.append(frame)

        return get_image_response(frames, transparency=255)
