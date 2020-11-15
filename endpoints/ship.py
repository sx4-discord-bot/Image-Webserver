from typing import List, Any

from PIL import Image

from handlers.handler import MultipleImageHandler
from utility.error import ErrorCode
from utility.image import create_avatar, get_image_asset, get_image_response
from utility.response import BadRequest


class ShipHandler(MultipleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries += [(["percent"], int)]

    def on_request(self, images: List[type(Image)]):
        first_image, second_image = images

        percent = self.query("percent", int)
        if percent > 100 or percent < 1:
            raise BadRequest("Percent cannot be larger than 100 or less than 1", ErrorCode.INVALID_QUERY_VALUE)

        blank = Image.new("RGBA", (930, 290), (255, 255, 255, 0))
        border = create_avatar(Image.new("RGBA", (290, 290), (255, 255, 255, 255)))

        heart, heart_outline = get_image_asset("heart.png"), get_image_asset("heart-outline.png")
        width, height = heart.size

        pixels = height - round(height / 100 * percent)

        heart = heart.crop((0, pixels, width, height))

        blank.paste(border, (0, 0), border)
        blank.paste(border, (640, 0), border)
        blank.paste(first_image, (5, 5), first_image)
        blank.paste(second_image, (645, 5), second_image)
        blank.paste(heart, (305, 0 + pixels), heart)
        blank.paste(heart_outline, (305, 0), heart_outline)

        return get_image_response([blank])

    def image_queries(self):
        return [("first_image", False), ("second_image", False)]

    def modify_images(self, images: List[type(Image)]) -> Any:
        return [create_avatar(image.convert("RGBA").resize((280, 280))) for image in images]
