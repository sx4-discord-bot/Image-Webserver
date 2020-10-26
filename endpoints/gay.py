from PIL import ImageSequence
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.image import get_image_asset, get_image, max_pixels, get_image_response
from utility.response import BadRequest


class GayHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

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
        overlay = get_image_asset("gay.png").resize(final_size)

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize(final_size)

            frame.paste(overlay, (0, 0), overlay)

            frames.append(frame)

        return get_image_response(frames, transparency=255)
