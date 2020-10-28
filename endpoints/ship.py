from PIL import Image, UnidentifiedImageError
from requests.exceptions import MissingSchema, ConnectionError

from handlers.handler import GetHandler
from utility.image import create_avatar, get_image_asset, get_image_response, get_image
from utility.response import BadRequest


class ShipHandler(GetHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["first_image"], str), (["second_image"], str), (["percent"], int)]

    def on_request(self):
        first_image_url = self.query("first_image")
        if not first_image_url:
            return BadRequest("first_image query not given")

        try:
            first_image = get_image(first_image_url)
        except MissingSchema:
            return BadRequest("Invalid first url")
        except UnidentifiedImageError:
            return BadRequest("First url could not be formed to an image")
        except ConnectionError:
            return BadRequest("Site took too long to respond")

        second_image_url = self.query("second_image")
        if not second_image_url:
            return BadRequest("second_image query not given")

        try:
            second_image = get_image(second_image_url)
        except MissingSchema:
            return BadRequest("Invalid second url")
        except UnidentifiedImageError:
            return BadRequest("Second url could not be formed to an image")
        except ConnectionError:
            return BadRequest("Site took too long to respond")

        percent = self.query("percent", int)
        if not percent:
            return BadRequest("Percent query is not a number or not given")

        if percent > 100 or percent < 1:
            return BadRequest("Percent cannot be larger than 100 or less than 1")

        blank = Image.new("RGBA", (930, 290), (255, 255, 255, 0))
        border = create_avatar(Image.new("RGBA", (290, 290), (255, 255, 255, 255)))

        heart, heart_outline = get_image_asset("heart.png"), get_image_asset("heart-outline.png")
        width, height = heart.size

        pixels = height - round(height / 100 * percent)

        heart = heart.crop((0, pixels, width, height))

        first_image = create_avatar(first_image.convert("RGBA").resize((280, 280)))
        second_image = create_avatar(second_image.convert("RGBA").resize((280, 280)))

        blank.paste(border, (0, 0), border)
        blank.paste(border, (640, 0), border)
        blank.paste(first_image, (5, 5), first_image)
        blank.paste(second_image, (645, 5), second_image)
        blank.paste(heart, (305, 0 + pixels), heart)
        blank.paste(heart_outline, (305, 0), heart_outline)

        return get_image_response([blank])