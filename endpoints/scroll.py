from PIL import ImageDraw

from handlers.handler import Handler
from utility.image import get_image_asset, get_font_asset, get_image_response, get_text_newlined


class ScrollHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.queries += [(["text"], str)]

    def on_request(self):
        text = self.query("text")

        background = get_image_asset("scroll-meme.png")
        font = get_font_asset("arialuni.ttf", 20)

        draw = ImageDraw.Draw(background)
        draw.text((95, 280), get_text_newlined(text, font, 90, 5), (0, 0, 0), font)

        return get_image_response([background])
