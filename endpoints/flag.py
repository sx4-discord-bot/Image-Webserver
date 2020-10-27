from io import BytesIO

import requests
from PIL import Image, ImageSequence, UnidentifiedImageError
from requests.exceptions import MissingSchema, ConnectionError

from handlers.handler import Handler
from utility.image import get_image, get_image_response, max_pixels
from utility.response import BadRequest


class FlagHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["image"], str), (["flag"], str)]

    def __call__(self):
        image_url = self.query("image")
        if not image_url:
            return BadRequest("Image query not given")

        try:
            image = get_image(image_url)
        except MissingSchema:
            return BadRequest("Invalid url")
        except UnidentifiedImageError:
            return BadRequest("Url could not be formed to an image")
        except ConnectionError:
            return BadRequest("Site took too long to respond")

        flag = self.query("flag")

        flag_response = requests.get(f"http://www.geonames.org/flags/x/{flag}.gif", stream=True)
        if flag_response.status_code == 404:
            return BadRequest("Invalid flag code")

        final_size = max_pixels(image.size, 200)
        flag_image = Image.open(BytesIO(flag_response.content)).convert("RGBA").resize(final_size)

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize(final_size)

            frames.append(Image.blend(frame, flag_image, 0.35))

        return get_image_response(frames, transparency=255)
