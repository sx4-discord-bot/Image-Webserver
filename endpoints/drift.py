from typing import Optional

from PIL import ImageDraw

from handlers.handler import SingleImageHandler
from utility.image import get_image_asset, get_font_asset, get_text_newlined, get_image_response, get_text_array


class DriftHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.queries += [(["left_text"], str), (["right_text"], Optional[str])]

    def on_request(self, avatar):
        left_text = self.query("left_text")
        right_text = self.query("right_text")

        background = get_image_asset("drift-meme.png")
        font = get_font_asset("arialuni.ttf", 20)

        background.paste(avatar, (270, 335), avatar)

        draw = ImageDraw.Draw(background)
        draw.text((125, 55), get_text_newlined(left_text, font, 80, 4), (255, 255, 255), font)

        if right_text:
            draw.text((265, 55), get_text_newlined(right_text, font, 110, 4), (255, 255, 255), font)

        return get_image_response([background])

    def modify_images(self, images):
        return images[0].convert("RGBA").resize((23, 23))
