from datetime import datetime
from typing import List, Any

from PIL import ImageDraw, Image

from handlers.handler import SingleImageHandler
from utility.image import get_image, get_font_asset, get_image_asset, get_text_array, get_image_response, create_avatar


class TweetHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["POST"]

        self.fields += [
            (["text"], str),
            (["likes"], int),
            (["retweets"], int),
            (["urls"], List[str]),
            (["name"], str),
            (["display_name"], str)
        ]

    def on_request(self, avatar):
        text = self.body("text")
        likes = f"{self.body('likes', int):,}"
        retweets = f"{self.body('retweets', int):,}"
        like_images = [create_avatar(get_image(url, f"urls.{i}", "field").convert("RGBA").resize((36, 36))) for i, url in enumerate(self.body("urls", list))]
        name = self.body("name")
        display_name = self.body("display_name")

        name_font = get_font_asset("gotham/Gotham-Black.otf", 25)
        tag_font = get_font_asset("gotham/GothamBook.ttf", 20)
        likes_font = get_font_asset("gotham/GothamBold.ttf", 21)
        text_font = get_font_asset("segoeuireg.ttf", 25)

        background = get_image_asset("tweet.png")
        draw = ImageDraw.Draw(background)

        lines = get_text_array(text, text_font, 833)

        height = 135
        for line in lines:
            width = 60

            text_split = line.split(" ")
            for word in text_split:
                word += " "
                colour = (0, 132, 180) if word.startswith("#") or word.startswith("@") else (0, 0, 0)
                draw.text((width, height), word, colour, text_font)
                width += text_font.getsize(word)[0]

            height += 30

        background.paste(avatar, (60, 44), avatar)
        draw.text((149, 47), display_name, (0, 0, 0), name_font)
        draw.text((149, 82), f"@{name}", (128, 128, 128), tag_font)

        retweets_width, likes_width = likes_font.getsize(retweets)[0], likes_font.getsize(likes)[0]
        retweets_text_width = tag_font.getsize("Retweets")[0]

        draw.text((59, 326), retweets, (0, 0, 0), likes_font)
        draw.text((64 + retweets_width, 327), "Retweets", (128, 128, 128), tag_font)
        draw.text((77 + retweets_width + retweets_text_width, 326), likes, (0, 0, 0), likes_font)
        draw.text((82 + retweets_width + retweets_text_width + likes_width, 327), "Likes", (128, 128, 128), tag_font)

        now = datetime.utcnow()
        draw.text((60, 270), f"{int(now.strftime('%I'))}{now.strftime(':%M %p - %d %b %Y')}", (128, 128, 128), tag_font)

        additional = 0
        for like_image in like_images:
            background.paste(like_image, (398 + additional, 317), like_image)
            additional += 44

        return get_image_response([background])

    def image_queries(self):
        return [("avatar", True)]

    def modify_images(self, images: List[type(Image)]) -> Any:
        return create_avatar(images[0].convert("RGBA").resize((72, 72)))
