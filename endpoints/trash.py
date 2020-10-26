from PIL import ImageSequence, ImageFilter
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.image import get_image, get_image_asset, get_image_response
from utility.response import BadRequest


class TrashHandler(Handler):

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

        background = get_image_asset("trash-meme.jpg")

        filter = ImageFilter.GaussianBlur(10)

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize((385, 384)).filter(filter)

            background = background.copy()
            background.paste(frame, (384, 0), frame)

            frames.append(background)

        return get_image_response(frames)
