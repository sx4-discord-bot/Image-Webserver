from PIL import ImageSequence
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.number import get_int, get_float
from utility.response import BadRequest


class ResizeHandler(Handler):

    def __call__(self):
        image_url = self.query("image")
        if not image_url:
            return BadRequest("Image query not given")

        try:
            image = self.get_image(image_url)
        except MissingSchema:
            return BadRequest("Url could not be formed to an image")
        except ConnectionError:
            return BadRequest("Site took too long to respond")

        width = self.query("width") or self.query("w")
        height = self.query("height") or self.query("h")

        width =  get_int(width) or get_float(width)
        height = get_int(height) or get_float(height)

        if not width or not height:
            return BadRequest("Width or Height query not given")

        if isinstance(width, float):
            width = round(float(width) * image.size[0])

        if isinstance(height, float):
            height = round(float(height) * image.size[1])

        if width < 1 or height < 1:
            return BadRequest("Width or Height is a negative number")

        frames = []
        for frame in ImageSequence.Iterator(image):
            frames.append(frame.resize((width, height)))

        return self.get_image_response(frames)