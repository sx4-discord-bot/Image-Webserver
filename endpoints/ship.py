from typing import List

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

        watermark = get_image_asset("watermark.png")

        heart, heart_outline = get_image_asset("heart.png"), get_image_asset("heart-outline.png")
        width, height = heart.size

        background = Image.new("RGBA", (930, 290), (0, 0, 0, 0))
        border = create_avatar(Image.new("RGBA", (290, 290), (255, 255, 255, 255)))
        background.paste(border, (0, 0), border)
        background.paste(border, (640, 0), border)

        pixels = height - round(height / 100 * percent)

        heart = heart.crop((0, pixels, width, height))

        first_frame_count, second_frame_count = first_image.n_frames, second_image.n_frames
        frame_count = max(first_frame_count, second_frame_count)

        frames = []
        for i in range(1):
            first_image.seek(i % first_frame_count)
            second_image.seek(i % second_frame_count)

            first_copy = create_avatar(first_image.convert("RGBA").resize((280, 280)))
            second_copy = create_avatar(second_image.convert("RGBA").resize((280, 280)))

            background = background.copy()

            background.paste(first_copy, (5, 5), first_copy)
            background.paste(second_copy, (645, 5), second_copy)
            background.paste(heart, (305, pixels), heart)
            background.paste(heart_outline, (305, 0), heart_outline)

            if self.authorization_type == "trial":
                background.paste(watermark, (0, 0), watermark)

            frames.append(background)

        return get_image_response(frames)

    def image_queries(self):
        return [("first_image", False, True), ("second_image", False, True)]