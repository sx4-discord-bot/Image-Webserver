from typing import Optional, Any, List

from PIL import Image, ImageDraw

from handlers.handler import SingleImageHandler
from utility.image import create_avatar, get_image, get_font_asset, get_image_response, for_each_frame, \
    get_font_optimal, resize_to_ratio
from utility.types import boolean


class WelcomerHandler(SingleImageHandler):

    DIRECTORY = "/root/{}/welcomer/banners/"

    def __init__(self, app):
        super().__init__(app)

        self.queries += [(["name"], str), (["gif"], bool), (["banner_id"], Optional[str]), (["directory"], str)]

    def on_request(self, avatar):
        name = self.query("name")
        banner_id = self.query("banner_id")
        directory = self.query("directory", str)
        gif = self.query("gif", boolean)

        welcome_font = get_font_asset("uni-sans.otf", 50)
        welcome_width = welcome_font.getsize("Welcome")[0]

        text_holder = Image.new("RGBA", (1280, 280), (0, 0, 0, 200))
        avatar_outline = create_avatar(Image.new("RGBA", (310, 310), (255, 255, 255)))

        split = name.split("#")
        name = split[0]
        discrim = "#" + split[1]

        discrim_width = welcome_font.getsize(discrim)[0]

        name_font = get_font_optimal("uni-sans.otf", 100, name, 1025 - discrim_width * 2)

        # very hacky way to vertically align the text
        name_width = name_font.getsize(name)[0]
        (_, _), (x, y) = name_font.font.getsize("a" * len(name))
        name_height = name_font.getmetrics()[0] - y

        if banner_id is not None:
            temp = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
            temp.paste(text_holder, (175, 220), text_holder)
            temp.paste(avatar_outline, (0, 205), avatar_outline)
            temp.paste(avatar, (5, 210), avatar)

            draw = ImageDraw.Draw(temp)
            draw.text(((1420 - welcome_width) / 2, 240), "Welcome", (255, 255, 255), welcome_font)
            draw.text(((1420 - name_width) / 2, 385 - name_height), name, (255, 255, 255), name_font)
            draw.text(((1420 - name_width) / 2 + name_width, 352), discrim, (153, 170, 183), welcome_font)

            with Image.open(WelcomerHandler.DIRECTORY.format(directory) + banner_id) as banner:
                def parse(frame):
                    frame = resize_to_ratio(frame.convert("RGBA"), (1280, 720))
                    frame.paste(temp, (0, 0), temp)

                    return frame

                return get_image_response(for_each_frame(banner, parse) if gif else [parse(banner)])
        else:
            banner = Image.new("RGBA", (1280, 310), (0, 0, 0, 0))
            banner.paste(text_holder, (175, 15), text_holder)
            banner.paste(avatar_outline, (0, 0), avatar_outline)
            banner.paste(avatar, (5, 5), avatar)

            draw = ImageDraw.Draw(banner)
            draw.text(((1420 - welcome_width) / 2, 35), "Welcome", (255, 255, 255), welcome_font)
            draw.text(((1420 - name_width) / 2, 180 - name_height), name, (255, 255, 255), name_font)
            draw.text(((1420 - name_width) / 2 + name_width, 147), discrim, (153, 170, 183), welcome_font)

            return get_image_response([banner])

    def image_queries(self):
        return [("avatar", False, True)]

    def modify_images(self, images: List[type(Image)]) -> Any:
        return create_avatar(images[0].convert("RGBA").resize((300, 300)))
