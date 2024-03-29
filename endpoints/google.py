from PIL import ImageDraw

from handlers.handler import Handler
from utility.image import get_image_asset, get_font_asset, get_image_response


class GoogleHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.queries = [(["query", "q"], str)]

    def on_request(self):
        query = self.query("q") or self.query("query")

        length = len(query)

        background = get_image_asset("google.png")
        font = get_font_asset("arialuni.ttf", 16)

        frames = []
        for i in range(0, length + 24):
            text = query[:i]

            copy = background.copy()
            draw = ImageDraw.Draw(copy)

            draw.text((378, 319), text, 0, font)

            if i < length:
                draw.text((378 + font.getsize(text)[0], 319), "|", 0, font)
            else:
                remaining = (i - length) % 6
                if remaining > 2:
                    draw.text((378 + font.getsize(text)[0], 319), "|", 0, font)

            frames.append(copy)

        return get_image_response(frames, transparency=255)
