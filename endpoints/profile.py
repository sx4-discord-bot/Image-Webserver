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
            (["is_birthday"], Optional[bool]),
            (["married_users"], List[str]),
            (["height"], int),
            (["reputation"], int),
            (["balance"], str),
            (["colour", "color"], int),
            (["commands"], int),
            (["games_played"], int),
            (["games_won"], int),
            (["banner_id"], Optional[str]),
            (["directory"], str),
            (["gif"], Optional[bool])
        ]

    def on_request(self, avatar: Image):
        name = self.body("name")
        description = self.body("description")
        birthday = self.body("birthday")
        is_birthday = self.body("is_birthday", bool, False)
        height = self.body("height", int)
        married_users = self.body("married_users", list)[:5]
        balance = self.body("balance")
        games_played = self.body("games_played", int)
        games_won = self.body("games_won", int)
        commands = self.body("commands", int)
        gif = self.body("gif", bool, False)
        banner_id = self.body("banner_id", str)
        directory = self.body("directory", str)
        reputation = self.body("reputation", int)
        colour_int = self.body("colour", int, 13997604) or self.body("color", int, 13997604)
        colour = as_rgb_tuple(colour_int)

        poppins_name = get_font_asset("poppins/Poppins-Medium.ttf", 40)
        poppins_title = get_font_asset("poppins/Poppins-Medium.ttf", 18)
        poppins_text = get_font_asset("poppins/Poppins-Medium.ttf", 21)
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
        limited_username = get_text_newlined(username, poppins_name, 480 - discrim_width, 1)

        draw.text((270, 56 - 18), "NAME", colour, poppins_title)
        draw.text((268, 99 - 40), limited_username + "#" + discrim, (247, 246, 245), poppins_name)

        draw.text((270, 142 - 18), "BIRTHDAY", colour, poppins_title)
        draw.text((270, 168 - 21), birthday, (247, 246, 245), poppins_text)

        draw.text((472, 142 - 18), "HEIGHT", colour, poppins_title)
        draw.text((472, 168 - 21), "Not set" if height == 0 else f"{height}cm", (247, 246, 245), poppins_text)

        draw.text((654, 142 - 18), "BALANCE", colour, poppins_title)
        draw.text((654, 168 - 21), balance, (247, 246, 245), poppins_text)

        draw.text((269, 218 - 18), "GAMES PLAYED", colour, poppins_title)
        draw.text((270, 244 - 21), f"{games_played:,}", (247, 246, 245), poppins_text)

        draw.text((471, 218 - 18), "GAMES WON", colour, poppins_title)
        draw.text((472, 244 - 21), f"{games_won:,}", (247, 246, 245), poppins_text)

        draw.text((653, 218 - 18), "COMMANDS USED", colour, poppins_title)
        draw.text((654, 244 - 21), f"{commands:,}", (247, 246, 245), poppins_text)

        draw.text((50, 294 - 18), "DESCRIPTION", colour, poppins_title)
        draw.text((50, 320 - 21), get_text_newlined(description, poppins_text, 500, 7), (247, 246, 245), poppins_text)

        draw.text((652, 294 - 18), "PARTNERS", colour, poppins_title)
        draw.text((652, 320 - 21), "\n".join([get_text_newlined(user, poppins_text, 250, 1) for user in married_users]) if len(married_users) > 0 else "No one :(", (247, 246, 245), poppins_text)

        draw_ellipse(card, (31, 31, 245, 245), 1, (255, 255, 255), 4)

        if is_birthday:
            cake = get_image_asset("cake.png")
            width, height = poppins_text.getsize(birthday)

            card.paste(cake, (275 + width, 168 - 21))

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
