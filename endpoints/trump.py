from PIL import ImageDraw

from handlers.handler import Handler
from utility.image import get_font_asset, get_image_asset, get_image_response, get_text_array


class TrumpTweetHandler(Handler):

    def __init__(self, app):
        super().__init__(app)

        self.queries += [(["text"], str)]

    def on_request(self):
        text = self.query("text")

        background = get_image_asset("trump-tweet-meme.png")
        font = get_font_asset("segoeuireg.ttf", 25)

        draw = ImageDraw.Draw(background)

        lines = get_text_array(text, font, 833)[:4]

        height = 125
        for line in lines:
            width = 60

            text_split = line.split(" ")
            for word in text_split:
                word += " "
                colour = (0, 132, 180) if word.startswith("#") or word.startswith("@") else (0, 0, 0)
                draw.text((width, height), word, colour, font)
                width += font.getsize(word)[0]

            height += 30

        return get_image_response([background])
