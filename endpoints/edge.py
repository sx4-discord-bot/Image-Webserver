from PIL import ImageSequence, ImageFilter
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.image import get_image, get_image_response
from utility.response import BadRequest


class EdgeHandler(Handler):

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

        filter = ImageFilter.FIND_EDGES

        frames = []
        for frame in ImageSequence.Iterator(image):
            frames.append(frame.convert("RGBA").filter(filter))

        return get_image_response(frames)
