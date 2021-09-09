from datetime import datetime
from typing import Dict, Optional, List

from PIL import ImageFont, Image, ImageDraw

from handlers.handler import SingleImageHandler
from utility.colour import as_rgb_tuple
from utility.error import ErrorCode
from utility.image import get_font_asset, get_image_asset, get_text_array, get_image_response, get_image, \
    for_each_frame, create_avatar
from utility.response import BadRequest


class TextType:

    # 0 = Text
    # 1 = User
    # 2 = Role
    # 3 = Channel
    # 4 = Emote

    def __init__(self, string: str, mention_type: int, discord_id: Optional[str], data: dict = None):
        self.string = string
        self.mention_type = mention_type
        self.discord_id = discord_id
        self.data = {} if data is None else data

    def width(self, font: ImageFont = None) -> int:
        return 30 if self.mention_type == 4 else font.getsize(self.string)[0]

    @property
    def mention(self):
        return self.mention_type != 0

    def __len__(self):
        return len(self.string)

    def __str__(self):
        return self.string


class DiscordHandler(SingleImageHandler):

    def __init__(self, app):
        super().__init__(app)

        self.methods = ["POST"]

        self.fields += [
            (["name"], str),
            (["colour", "color"], int),
            (["text"], str),
            (["dark_theme"], bool),
            (["bot"], bool),
            (["emotes"], List[str]),
            (["roles"], Dict[str, Dict[str, object]]),
            (["users"], Dict[str, Dict[str, object]]),
            (["channels"], Dict[str, Dict[str, object]])
        ]

    def on_request(self, avatar):
        name = self.body("name")
        colour = as_rgb_tuple(self.body("colour", int) or self.body("color", int))
        text = self.body("text")
        bot = self.body("bot", bool)
        dark_theme = self.body("dark_theme", bool)
        emotes = self.body("emotes", list)
        roles = self.body("roles", dict)
        users = self.body("users", dict)
        channels = self.body("channels", dict)

        if len(text) > 250:
            raise BadRequest("Text at max can be 250 characters in length", ErrorCode.INVALID_FIELD_VALUE)

        mention_font = get_font_asset("whitney/Whitney-Medium.ttf", 34)
        text_font = get_font_asset("whitney/whitney-book.otf", 34)
        time_font = get_font_asset("whitney/WhitneyLight.ttf", 24)

        bot_tag = get_image_asset("bot-tag.png")

        text_types = []
        builder = []

        i = 0
        while i < len(text):
            character = text[i]
            if character == "<" and i + 2 < len(text):
                first_character = text[i + 1]
                second_character = text[i + 2]
                greater_index = text.find(">", i)

                if greater_index != -1:
                    if first_character == "@" and second_character == "&":
                        role_id = text[i + 3:greater_index]
                        if role_id.isdigit() and role_id in roles.keys():
                            role = roles.get(role_id)

                            text_types.append(TextType("".join(builder), 0, None))
                            builder = []
                            text_types.append(TextType(f"@{role.get('name')}", 2, role_id, role))
                            i = greater_index + 1
                            continue
                    elif first_character == "@":
                        user_id = text[i + (3 if second_character == "!" else 2):greater_index]
                        if user_id.isdigit() and user_id in users.keys():
                            text_types.append(TextType("".join(builder), 0, None))
                            builder = []
                            text_types.append(TextType(f"@{users.get(user_id).get('name')}", 1, user_id))
                            i = greater_index + 1
                            continue
                    elif first_character == "#":
                        channel_id = text[i + 2:greater_index]
                        if channel_id.isdigit() and channel_id in channels.keys():
                            text_types.append(TextType(f"#{channels.get(channel_id).get('name')}", 3, channel_id))
                            builder = []
                        else:
                            builder.append("#deleted-channel")

                        i = greater_index + 1
                        continue
                    elif first_character == ":" or second_character == ":":
                        image_type = "gif" if second_character == ":" and first_character == "a" else "png"
                        colon_index = text.find(":", i + 3)
                        emote_id = text[colon_index + 1:greater_index]
                        if emote_id.isdigit() and emote_id in emotes:
                            text_types.append(TextType("".join(builder), 0, None))
                            builder = []
                            text_types.append(
                                TextType(f"https://cdn.discordapp.com/emojis/{emote_id}.{image_type}", 4, emote_id))
                            i = greater_index + 1
                            continue

            builder.append(character)
            i += 1

        if len(builder) != 0:
            text_types.append(TextType("".join(builder), 0, None))

        blank = Image.new("RGBA", (1000, 400), (0, 0, 0, 0))

        draw = ImageDraw.Draw(blank)

        name_width = mention_font.getsize(name)[0]
        draw.text((160, 9), name, colour, mention_font)
        draw.text((167 + name_width + (66 if bot else 0), 18), f"Today at {datetime.utcnow().strftime('%H:%M')}", (114, 118, 125), time_font)

        if bot:
            blank.paste(bot_tag, (167 + name_width, 2), bot_tag)

        width, height = 0, 50
        for text_type in text_types:
            if text_type.mention:
                text_type_width = text_type.width(text_font)
                if width + text_type_width > 820:
                    width = 0
                    height += 34

                colour = text_type.data.get("colour")
                if text_type.mention_type == 2 and colour is not None:
                    mention_colour = as_rgb_tuple(colour)
                    mention_box_colour = mention_colour + (26,)
                    text_colour = mention_colour
                else:
                    mention_box_colour = (88, 101, 242, 77) if dark_theme else (88, 101, 242, 38)
                    text_colour = (222, 224, 252) if dark_theme else (80, 92, 220)

                if text_type.mention_type == 4:
                    emote = get_image(str(text_type)).convert("RGBA").resize((30, 30))
                    blank.paste(emote, (width + 160, height + 6), emote)
                else:
                    draw.rectangle((width + 160, height + 5, width + 160 + text_type_width, height + 37), mention_box_colour)
                    draw.text((width + 160, height), str(text_type), text_colour, mention_font)

                width += text_type_width
            else:
                lines = get_text_array(str(text_type), text_font, 820, width, False)
                for i, line in enumerate(lines):
                    draw.text((width + 160, height), line, (220, 221, 222) if dark_theme else (116, 127, 141), text_font)

                    if i == len(lines) - 1:
                        width += text_font.getsize(line)[0]
                    else:
                        if i == 0:
                            width = 0

                        height += 34

        background = Image.new("RGBA", (1000, max(height + 42, 120)), (54, 57, 63) if dark_theme else (255, 255, 255))
        background.paste(blank, (0, 0), blank)

        def parse(frame):
            frame = create_avatar(frame.convert("RGBA").resize((100, 100)))

            copy = background.copy()
            copy.paste(frame, (20, 10), frame)

            return copy

        return get_image_response(for_each_frame(avatar, parse), transparency=255)

    def image_queries(self):
        return [("avatar", True, False)]
