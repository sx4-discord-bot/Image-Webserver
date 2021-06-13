from io import BytesIO

import numpy as np
from typing import List, Optional, Any

from PIL import Image, ImageDraw

from handlers.handler import SingleImageHandler
from utility.colour import as_rgb_tuple
from utility.image import create_avatar, get_image_response, get_image_asset, get_font_optimal, get_font_asset, \
    get_text_newlined, resize_to_ratio, draw_ellipse, for_each_frame
from utility.types import boolean


class ProfileHandler(SingleImageHandler):

    DIRECTORY = "/root/{}/profile/banners/"

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["POST"]

        self.fields += [
            (["name"], str),
            (["description"], str),
            (["birthday"], str),
            (["married_users"], List[str]),
            (["height"], int),
            (["reputation"], int),
            (["balance"], str),
            (["colour", "color"], int),
            (["banner_id"], Optional[str]),
            (["directory"], str),
            (["gif"], Optional[bool])
        ]

    def on_request(self, avatar: Image):
        name = self.body("name")
        description = self.body("description")
        birthday = self.body("birthday")
        height = self.body("height", int)
        married_users = self.body("married_users", list)[:5]
        balance = self.body("balance")
        gif = self.body("gif", bool, False)
        banner_id = self.body("banner_id", str)
        directory = self.body("directory", str)
        reputation = self.body("reputation", int)
        colour_int = self.body("colour", int, 13997604) or self.body("color", int, 13997604)
        colour = as_rgb_tuple(colour_int)

        poppins_name = get_font_asset("poppins/Poppins-Medium.ttf", 42)
        poppins_title = get_font_asset("poppins/Poppins-Medium.ttf", 20)
        poppins_text = get_font_asset("poppins/Poppins-Medium.ttf", 23)
        poppins_rep = get_font_asset("poppins/Poppins-Medium.ttf", 32)

        card = Image.new("RGBA", (935, 567), (0, 0, 0, 0))

        draw = ImageDraw.Draw(card)

        # Horizontal lines
        draw.line((0, 11, 935, 11), colour, 24)
        draw.line((0, 567 - 12, 935, 567 - 12), colour, 24)

        # Vertical lines
        draw.line((11, 0, 11, 567), colour, 24)
        draw.line((935 - 12, 0, 935 - 12, 567), colour, 24)

        reputation_width, reputation_height = draw.textsize(str(reputation), poppins_rep)
        total_width = 34 + reputation_width + 4

        draw.rectangle((935 - 188, 0, 935, 63), colour)
        draw.text(((935 - 202) + ((188 - total_width) / 2), 7), str(reputation), (255, 250, 245), poppins_rep)
        draw.text(((935 - 198) + ((188 - total_width) / 2) + reputation_width, 6), "REP", (41, 40, 39), poppins_rep)

        username, discrim = name.split("#")
        discrim_width, discrim_height = draw.textsize("#" + discrim, poppins_name)
        limited_username = get_text_newlined(username, poppins_name, 620 - discrim_width, 1)

        draw.text((270, 78 - 20), "NAME", colour, poppins_title)
        draw.text((268, 125 - 42), limited_username + "#" + discrim, (247, 246, 245), poppins_name)

        draw.text((270, 172 - 20), "BIRTHDAY", colour, poppins_title)
        draw.text((270, 204 - 23), birthday, (247, 246, 245), poppins_text)

        draw.text((472, 172 - 20), "HEIGHT", colour, poppins_title)
        draw.text((472, 202 - 23), f"{height}cm", (247, 246, 245), poppins_text)

        draw.text((654, 169 - 20), "BALANCE", colour, poppins_title)
        draw.text((654, 202 - 23), f"${balance}", (247, 246, 245), poppins_text)

        draw.text((50, 293 - 20), "DESCRIPTION", colour, poppins_title)
        draw.text((50, 320 - 23), get_text_newlined(description, poppins_text, 500, 7), (247, 246, 245),
                  poppins_text)

        draw.text((652, 293 - 20), "PARTNERS", colour, poppins_title)
        draw.text((652, 320 - 23), "\n".join(
            [get_text_newlined(user, poppins_text, 250, 1) for user in married_users]) if len(
            married_users) > 0 else "No one :(", (247, 246, 245), poppins_text)

        draw_ellipse(card, (31, 31, 245, 245), 1, (255, 255, 255), 4)

        card.paste(avatar, (34, 34), avatar)

        if banner_id is None:
            image = Image.new("RGBA", (935, 567), (41, 40, 39))
            image.paste(card, (0, 0), card)
            return get_image_response([image])
        else:
            with Image.open(ProfileHandler.DIRECTORY.format(directory) + banner_id) as image:
                def parse(frame):
                    frame = resize_to_ratio(frame.convert("RGBA"), (935, 567))

                    overlay = Image.new("RGBA", frame.size, (41, 40, 39, 0))
                    draw = ImageDraw.Draw(overlay)
                    draw.rectangle((0, 567, 935, 0), (41, 40, 39, 216))

                    frame = Image.alpha_composite(frame, overlay)
                    frame.paste(card, (0, 0), card)

                    return frame

                return get_image_response(for_each_frame(image, parse) if gif else [parse(image)], transparency=255)



    def image_queries(self):
        return [("avatar", True, True)]

    def modify_images(self, images):
        return create_avatar(images[0].convert("RGBA").resize((208, 208), Image.ANTIALIAS))
