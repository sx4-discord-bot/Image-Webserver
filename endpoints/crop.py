from PIL import ImageSequence
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.image import get_image, get_image_response
from utility.number import get_float
from utility.response import BadRequest


class CropHandler(Handler):

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

        image_width, image_height = image.size

        width = get_float(self.query("width") or self.query("w"))
        height = get_float(self.query("height") or self.query("h"))

        if not width and not height:
            return BadRequest("width and height query not given")

        width = width if width else image_width
        height = height if height else image_height

        if width <= 1:
            width = round(width * image_width)

        if height <= 1:
            height = round(height * image_height)

        if width < 1 or height < 1:
            return BadRequest("width or height is a negative number")

        if width > image_width or height > image_height:
            return BadRequest("width or height is larger than original width/height")

        left = image_width / 2 - width / 2
        upper = image_height / 2 - height / 2

        frames = []
        for frame in ImageSequence.Iterator(image):
            frames.append(frame.crop((left, upper, width + left, height + upper)))

        return get_image_response(frames)
