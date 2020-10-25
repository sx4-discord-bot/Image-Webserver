from PIL import ImageSequence
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.image import get_image, get_image_asset, get_image_response
from utility.response import BadRequest


class FearHandler(Handler):

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

        background = get_image_asset("fear-meme.png")

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize((251, 251))

            background = background.copy()
            background.paste(frame, (260, 517), frame)

            frames.append(background)

        print(len(frames))

        return get_image_response(frames)
