from PIL import Image, ImageSequence
from requests.exceptions import MissingSchema, ConnectionError

from handler import Handler
from utility.image import get_image, get_image_asset, get_image_response
from utility.response import BadRequest


class ShitHandler(Handler):

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

        blank = Image.new("RGBA", (763, 1000), (255, 255, 255, 0))
        background = get_image_asset("shit-meme.png")

        frames = []
        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA").resize((185, 185)).rotate(50, expand=True)

            blank = blank.copy()
            blank.paste(frame, (215, 675), frame)
            blank.paste(background, (0, 0), background)

            frames.append(blank)

        return get_image_response(frames, transparency=255)
