from PIL import ImageSequence, Image, UnidentifiedImageError
from requests.exceptions import MissingSchema, ConnectionError

from handlers.handler import Handler
from utility.image import get_image, get_image_asset, get_image_response

from utility.response import BadRequest


class HotHandler(Handler):

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
            return BadRequest("Invalid url")
        except UnidentifiedImageError:
            return BadRequest("Url could not be formed to an image")
        except ConnectionError:
            return BadRequest("Site took too long to respond")

        background = get_image_asset("thats-hot-meme.png")
        blank = Image.new("RGBA", background.size, (255, 255, 255, 0))

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize((400, 300))

            blank = blank.copy()
            blank.paste(frame, (8, 213), frame)
            blank.paste(background, (0, 0), background)

            frames.append(blank)

        return get_image_response(frames, transparency=255)
