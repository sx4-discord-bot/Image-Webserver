from io import BytesIO

import numpy as np
from typing import List, Optional, Any

from PIL import Image, ImageDraw

from handlers.handler import SingleImageHandler
from utility.colour import as_rgb_tuple
from utility.image import create_avatar, get_image_response, get_image_asset, get_font_optimal, get_font_asset, \
    get_text_newlined


class ProfileHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["POST"]

        self.fields += [
            (["name"], str),
            (["description"], str),
            (["birthday"], str),
            (["background"], Optional[bytes]),
            (["married_users"], List[str]),
            (["height"], str),
            (["reputation"], int),
            (["balance"], str),
            (["colour", "color"], int),
            (["badges"], List[str])
        ]

    def on_request(self, avatar):
        name = self.body("name")
        description = self.body("description")
        birthday = self.body("birthday")
        height = self.body("height")
        married_users = self.body("married_users", list)[:5]
        balance = self.body("balance")
        background = self.body("background", list)
        background = None if background is None else BytesIO(bytearray([x % 256 for x in background]))
        reputation = self.body("reputation", int)
        colour = as_rgb_tuple(self.body("colour", int, 16777215) or self.body("color", int, 16777215))
        badges = self.body("badges", list)

        blank = Image.new("RGBA", (2560, 1440), (255, 255, 255, 0))

        if background:
            background = Image.open(background).convert("RGBA")
        else:
            background = Image.new("RGBA", (2560, 1440), (114, 137, 218))

        blank.paste(background, (0, 0), background)

        avatar_outline = create_avatar(Image.new("RGBA", (470, 470), colour))

        draw = ImageDraw.Draw(blank)
        draw.rectangle((0, 0, 2000, 500), (35, 39, 42))
        draw.rectangle((0, 500, 2000, 650), (44, 47, 51))
        draw.rectangle((2000, 0, 2560, 650), (44, 47, 51))
        draw.rectangle((70, 750, 1070, 1350), (0, 0, 0, 175))
        draw.rectangle((1490, 750, 2490, 1350), (0, 0, 0, 175))

        # Box 1 vertical borders
        draw.line((74, 750, 74, 1350), colour, 10)
        draw.line((1075, 750, 1075, 1350), colour, 10)

        # Box 1 horizontal borders
        draw.line((70, 754, 1070, 754), colour, 10)
        draw.line((70, 1355, 1080, 1355), colour, 10)

        # Box 2 horizontal borders
        draw.line((1490, 754, 2490, 754), colour, 10)
        draw.line((1490, 1355, 2500, 1355), colour, 10)

        # Box 2 vertical borders
        draw.line((1494, 750, 1494, 1350), colour, 10)
        draw.line((2495, 750, 2495, 1350), colour, 10)

        # Skeleton
        draw.line((0, 505, 2000, 505), colour, 10)
        draw.line((0, 655, 2560, 655), colour, 10)
        draw.line((2005, 0, 2005, 650), colour, 10)

        # Vertical borders
        draw.line((500, 510, 500, 650), colour, 10)
        draw.line((1000, 510, 1000, 650), colour, 10)
        draw.line((1500, 510, 1500, 650), colour, 10)

        name_font = get_font_optimal("exo.regular.otf", 216, name, 1435)
        stats_font = get_font_asset("exo.regular.otf", 45)
        title_font = get_font_asset("exo.regular.otf", 70)

        name_width, name_height = name_font.getsize(name)

        draw.text(((2000 - name_width) / 2 + 215, 250 - name_height / 2), name, colour, name_font)
        draw.text((20, 555), f"Reputation: {reputation}", colour, stats_font)
        draw.text((520, 555), f"Balance: ${balance}", colour, stats_font)
        draw.text((1020, 555), f"Birthday: {birthday}", colour, stats_font)
        draw.text((1520, 555), f"Height: {height}", colour, stats_font)

        draw.text((2160, 20), "Badges", colour, title_font)
        draw.text((95, 770), "Description", colour, title_font)
        draw.text((1515, 770), "Partners", colour, title_font)

        draw.text((95, 870), get_text_newlined(description, stats_font, 950, 11), colour, stats_font)

        partners = "\n".join([f"• {user}\n" for user in married_users]) if len(married_users) > 0 else "No one :("
        draw.text((1515, 870), partners, colour, stats_font)

        width, height = 2030, 130
        for badge in badges:
            badge_image = get_image_asset(f"badges/{badge}.png")
            blank.paste(badge_image, (width, height), badge_image)

            if width + 130 >= 2550:
                width = 2030
                height += 120
            else:
                width += 130

        blank.paste(avatar_outline, (15, 15), avatar_outline)
        blank.paste(avatar, (25, 25), avatar)

        blank = Image.alpha_composite(background, blank)

        return get_image_response([blank])

    def image_queries(self):
        return [("avatar", True)]

    def modify_images(self, images):
        return create_avatar(images[0].convert("RGBA").resize((450, 450)))
